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
        # original
        #if row.empty:
        #    return 'DataFrameEditorDefault'

        #for _, decision_row in decision_table.iterrows():
        #    if all(self._check_condition(row.get(col, pd.NA), decision_row[col]) for col in row.index):
        #        result = decision_row['DecisionResult']
        #        msg = f"All conditions met, returning DecisionResult: {result}"
        #        self.log_msg(msg, LogLevel.INFO)
        #        return result
        #msg = "No matching conditions found, returning DataFrameEditorDefault"
        #self.log_msg(msg, LogLevel.INFO)
        #return 'DataFrameEditorDefault'

        # debug add v1
        #if row.empty:
        #    return 'DataFrameEditorDefault'

        #for idx, decision_row in decision_table.iterrows():
        #    # 各列の条件チェック結果を収集
        #    conditions_results = {}
        #    all_matched = True
        #    
        #    for col in row.index:
        #        value = row.get(col, pd.NA)
        #        condition = decision_row[col]
        #        is_matched = self._check_condition(value, condition)
        #        
        #        conditions_results[col] = {
        #            'value': value,
        #            'condition': condition,
        #            'matched': is_matched
        #        }
        #        
        #        if not is_matched:
        #            all_matched = False
        #            break
        #    
        #    # デバッグ情報をログ出力
        #    self.log_msg(f"\nDecision table row {idx} evaluation:", LogLevel.DEBUG)
        #    for col, result in conditions_results.items():
        #        self.log_msg(
        #            f"Column: {col} - Value: {result['value']} vs. "
        #            f"Condition: {result['condition']} -->  Matched: {result['matched']}", 
        #            LogLevel.DEBUG
        #        )
        #    
        #    if all_matched:
        #        result = decision_row['DecisionResult']
        #        self.log_msg(f"All conditions met for row {idx}, result: {result}", LogLevel.INFO)
        #        return result

        #return 'DataFrameEditorDefault'

        # debug add v2
        if row.empty:
            self.log_msg("Empty row received, returning default", LogLevel.INFO)
            return 'DataFrameEditorDefault'

        for idx, decision_row in decision_table.iterrows():
            conditions_results = {}
            all_matched = True
            
            # 条件チェック結果の収集
            for col in row.index:
                value = row.get(col, pd.NA)
                condition = decision_row[col]
                
                try:
                    is_matched = self._check_condition(value, condition)
                    check_method = self._get_check_method_name(condition)
                    
                    conditions_results[col] = {
                        'value': value,
                        'condition': condition,
                        'matched': is_matched,
                        'check_method': check_method
                    }
                    
                    if not is_matched:
                        all_matched = False
                        break
                        
                except Exception as e:
                    self.log_msg(f"Error checking condition for column {col}: {str(e)}", LogLevel.ERROR)
                    raise

            # デバッグ情報のログ出力
            self._log_evaluation_results(idx, conditions_results)
            
            if all_matched:
                result = decision_row['DecisionResult']
                self.log_msg(
                    f"Match found in row {idx}: {result}",
                    LogLevel.INFO
                )
                return result

        self.log_msg("No matching conditions found, returning default", LogLevel.INFO)
        return 'DataFrameEditorDefault'

    def _get_check_method_name(self, condition: str|int) -> str:
        """条件チェックの種類を判定して返す"""
        if pd.isna(condition):
            return 'na_check'
        if condition == "any":
            return 'any_check'
        if isinstance(condition, str):
            if "," in condition:
                return 'or_condition'
            if condition in self.dt_functions:
                return 'dt_function'
            if self.is_regex(condition):
                return 'regex'
        return 'direct_comparison'

    def _log_evaluation_results(self, idx: int, results: dict) -> None:
        """評価結果のログ出力を行う"""
        self.log_msg(f"\nDecision table row {idx} evaluation:", LogLevel.DEBUG)
        for col, result in results.items():
            self.log_msg(
                f"Column: {col} | "
                f"Value: {result['value']} | "
                f"Condition: {result['condition']} | "
                f"Method: {result['check_method']} | "
                f"Matched: {result['matched']}", 
                LogLevel.DEBUG
            )



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
