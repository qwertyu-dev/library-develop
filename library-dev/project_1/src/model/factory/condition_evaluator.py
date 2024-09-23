import pandas as pd

from src.lib.common_utils.ibr_enums import LogLevel
from src.lib.common_utils.ibr_decorator_config import with_config
from src.lib.validator_utils.ibr_decision_table_validator import DT

@with_config
class ConditionEvaluator:
    def __init__(self):
        self.dt_functions = {func: getattr(DT, func) for func in dir(DT) if callable(getattr(DT, func)) and not func.startswith("__")}
        self.log_msg = self.config.log_message

    def evaluate_conditions(self, row: pd.Series, decision_table: pd.DataFrame) -> str:
        for _, decision_row in decision_table.iterrows():
            if all(self._check_condition(row[col], decision_row[col]) for col in row.index):
                result = decision_row['DecisionResult']
                msg = f"All conditions met, returning DecisionResult: {result}"
                self.log_msg(msg, LogLevel.INFO)
                return result
        msg = "No matching conditions found, returning DataFrameEditorDefault"
        self.log_msg(msg, LogLevel.INFO)
        return 'DataFrameEditorDefault'

    def _check_condition(self, value: str|int, condition: str|int) -> bool:
        if pd.isna(condition) or condition == "any":
            return True

        if isinstance(condition, str):
            if condition in self.dt_functions:
                return self._check_dt_function(value, condition)
            if "," in condition:
                return self._check_or_condition(value, condition)

        return str(value) == str(condition)

    def _check_dt_function(self, value: str|int, condition: str) -> bool:
        result = self.dt_functions[condition](value)
        self.log_msg(f"DT function {condition} result: {result}", LogLevel.DEBUG)
        return result

    def _check_or_condition(self, value: str|int, condition: str) -> bool:
        conditions = [c.strip() for c in condition.split(',')]
        return any(self._check_condition(value, c) for c in conditions)
