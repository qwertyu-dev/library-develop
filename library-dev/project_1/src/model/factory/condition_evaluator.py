import pandas as pd
import re

from src.lib.common_utils.ibr_enums import LogLevel
from src.lib.common_utils.ibr_decorator_config import with_config
from src.lib.validator_utils.ibr_decision_table_validator import DT


class ReExceptionError(Exception):
    pass
    
@with_config
class ConditionEvaluator:
    def __init__(self, config: dict|None = None):
        self.config = config or self.config
        self.dt_functions = {func: getattr(DT, func) for func in dir(DT) if callable(getattr(DT, func)) and not func.startswith("__")}
        self.log_msg = self.config.log_message

    def evaluate_conditions(self, row: pd.Series, decision_table: pd.DataFrame) -> str:
        if row.empty:
            return 'DataFrameEditorDefault'

        for _, decision_row in decision_table.iterrows():
            if all(self._check_condition(row.get(col, pd.NA), decision_row[col]) for col in row.index):
                result = decision_row['DecisionResult']
                msg = f"All conditions met, returning DecisionResult: {result}"
                self.log_msg(msg, LogLevel.INFO)
                return result
        msg = "No matching conditions found, returning DataFrameEditorDefault"
        self.log_msg(msg, LogLevel.INFO)
        return 'DataFrameEditorDefault'

    def _check_condition(self, value: str|int, condition: str|int) -> bool:
        if pd.isna(condition) :
            return False

        if condition == "any":
            return True

        if isinstance(condition, str):
            if "," in condition:
                return self._check_or_condition(value, condition)
            if condition in self.dt_functions:
                return self._check_dt_function(value, condition)
            if self.is_regex(condition):
                return self._check_regex(value, condition)

        return str(value) == str(condition)

    def is_regex(self, condition: str) -> bool:
        if not condition:   # 空の条件の場合は False を返す
            return False
        try:
            re.compile(condition)
        except re.error:
            return False
        except ReExceptionError:
            return False
        else:
            return True

    def _check_regex(self, value: str|int, condition: str) -> bool:
        if not condition:  # 空の正規表現パターンの場合は False を返す
            return False

        if isinstance(value, str|int):
            value = str(value)
            match = re.match(condition, value)
            self.log_msg(f'Regex {condition}: match result: {bool(match)}', LogLevel.DEBUG)
            return bool(match)
        return False

    def _check_dt_function(self, value: str|int, condition: str) -> bool:
        result = self.dt_functions[condition](value)
        self.log_msg(f"DT function {condition} result: {result}", LogLevel.DEBUG)
        return result

    def _check_or_condition(self, value: str|int, condition: str) -> bool:
        if not condition:  # 空の条件文字列の場合は False を返す
            return False

        conditions = [c.strip() for c in condition.split(',')]
        self.log_msg(f"conditions {conditions}", LogLevel.INFO)

        for c in conditions:
            if c in self.dt_functions and self.dt_functions[c](value):
                return True
            if self.is_regex(c) and self._check_regex(value, c):
                return True
            if str(value) == str(c):
                return True
        return False
