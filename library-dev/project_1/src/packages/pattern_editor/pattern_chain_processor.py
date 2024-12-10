import sys
import pandas as pd
from src.lib.common_utils.ibr_decorator_config import initialize_config
from src.lib.common_utils.ibr_pickled_table_searcher import TableSearcher
from src.model.processor_chain.processor_interface import PostProcessor, PreProcessor, ProcessorChain
from .data_validator_pattern_editor import DataValidator
from .validation_models_pattern_editor import PatternEditModel

config = initialize_config(sys.modules[__name__])
package_config = config.package_config
log_msg = config.log_message

# Package config
decision_table_path = package_config.get('pattern_editor_input', {}).get('PATTERN_EDITOR_DECISION_INPUT_PATH', '')
decision_table_file = package_config.get('pattern_editor_input', {}).get('PATTERN_EDITOR_DECISION_INPUT_PICKLE', '')
request_list_table_path = package_config.get('pattern_editor_input', {}).get('PATTERN_EDITOR_INPUT_PATH', '')
request_list_table_file = package_config.get('pattern_editor_input', {}).get('PATTERN_EDITOR_INPUT_PICKLE', '')
pattern_edited = package_config.get('pattern_editor_output', {}).get('PATTERN_EDITOR_OUTPUT_PICKLE', '')
debug_pattern_result_xlsx = package_config.get('pattern_debug', {}).get('PATTERN_EDITOR_RESULT_EXCEL_FILE', '')

# Decision table mapping
decision_table_columns_def = package_config.get('decision_table_layout', {}).get('DECISION_TABLE_COLUMNS', '')
columns_to_transform_def = package_config.get('decision_table_layout', {}).get('COLUMNS_TO_TRANSFORM', '')
decision_table_columns_fin_def = package_config.get('decision_table_layout', {}).get('DECISION_TABLE_COLUMNS_FIN', '')

class PatternChainProcessorError(Exception):
    pass

class PreProcessorDecisionTable(PreProcessor):
    def chain_pre_processor(self) -> list[PreProcessor]:
        return [
            ReadDecisionTable(),
            ModifyDecisionTable(),
        ]

class PreProcessorRequest(PreProcessor):
    def chain_pre_processor(self) -> list[PreProcessor]:
        return [
            ReadRequestListTable(),
            AddDecisionJudgeColumns(),
        ]

class PostProcessorRequest(PostProcessor):
    def chain_post_processor(self) -> list[PostProcessor]:
        return [
            ValidationResult(),
            WritePatternResult(),
        ]

class ReadDecisionTable(PreProcessor):
    def process(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()
        try:
            decision = TableSearcher(decision_table_file, decision_table_path)
        except Exception as e:
            err_msg = f'パターン編集処理 DecisionTable読み込みで失敗が発生しました: {str(e)}'
            raise PatternChainProcessorError(err_msg) from None
        else:
            return decision.df.fillna('')

class ModifyDecisionTable(PreProcessor):
    def process(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()
        df.columns = decision_table_columns_def
        for col in columns_to_transform_def:
            df[col] = self._replace_values(df[col])
        return df.loc[:, decision_table_columns_fin_def]

    def _replace_values(self, column):
        column = column.replace('4桁', 'is_4digits')
        column = column.replace('5桁', 'is_5digits')
        column = column.replace('なし', 'is_empty')
        column = column.replace('あり', 'is_not_empty')
        column = column.replace('BPR・AD対象外', 'is_not_bpr_ad_target', regex=True)
        column = column.replace('BPR・AD対象', 'is_bpr_ad_target', regex=True)
        column = column.replace('ADのみ対象', 'is_ad_only_target', regex=True)
        column = column.replace(r'^-$', 'any', regex=True)
        return column

class ReadRequestListTable(PreProcessor):
    def process(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()
        try:
            request_list_table = TableSearcher(request_list_table_file)
        except Exception as e:
            err_msg = f'変更情報テーブルファイル読み込みで失敗が発生しました: {str(e)}'
            raise PatternChainProcessorError(err_msg) from None
        else:
            return request_list_table.df.fillna('')

class AddDecisionJudgeColumns(PreProcessor):
    def process(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()
        return self._add_decision_table_columns(df)

    def _add_decision_table_columns(self, df):
        df['parent_branch_code'] = df['parent_branch_code'].astype(str)
        df['branch_code'] = df['branch_code'].astype(str)
        df['specific_department_code'] = df['branch_code']
        df['branch_code_first_2_digit'] = df['branch_code'].astype(str).str[:2]
        #df['parent_branch_code_and_branch_code_first_4_digits_match'] = df.apply(
        #    lambda row: 'exists' if row['parent_branch_code'] == row['branch_code'][:4] else '', axis=1)
        df['parent_branch_code_and_branch_code_first_4_digits_match'] = (df['parent_branch_code'] == df['branch_code'].str[:4]).map({True: 'exists', False: ''})
        return df

class ValidationResult(PostProcessorRequest):
    def process(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()
        try:
            data_validator = DataValidator(config, PatternEditModel)
            data_validator.validate(df)
        except Exception as e:
            err_msg = f'パターン編集処理結果のValidationに失敗が発生しました: {str(e)}'
            raise PatternChainProcessorError(err_msg) from None
        return df

class WritePatternResult(PostProcessorRequest):
    def process(self, df: pd.DataFrame) -> None:
        df = df.copy()
        try:
            df.to_pickle(pattern_edited)
            df = df.astype(str)
            df.to_excel(debug_pattern_result_xlsx, index=None)
        except Exception as e:
            err_msg = f'パターン編集処理結果ファイル書き込みで失敗が発生しました: {str(e)}'
            raise PatternChainProcessorError(err_msg) from None
