import re
import sys
import pandas as pd
from src.lib.common_utils.ibr_dataframe_helper import tabulate_dataframe
from src.lib.common_utils.ibr_decorator_config import initialize_config
from src.lib.common_utils.ibr_enums import ApplicationType, LogLevel, OrganizationType
from src.lib.common_utils.ibr_pickled_table_searcher import TableSearcher
from src.lib.converter_utils.ibr_bpr_flag_determiner import (
    AlertCode,
    BprAdFlagDeterminer,
    BprFragDeterminerError,
    BprTargetConfig,
    ValidationConfig,
)
from src.lib.converter_utils.ibr_reference_mergers import (
    BranchNameSplitError,
    DataLoadError,
    DataMergeError,
    MergerConfig,
    ReferenceColumnConfig,
    ReferenceMergers,
    ReferenceMergersError,
    RemarksParseError,
)
from src.lib.converter_utils.ibr_reference_pre_mapping import (
    AreaGroupInfo,
    BranchNameSplitError,
    DataLoadError,
    DataMergeError,
    MergerConfig,
    ParsedRemarks,
    PreparationPreMapping,
    ReferenceMergersError,
    RemarksParseError,
    SalesDepartmentInfo,
)
from src.model.processor_chain.processor_interface import PostProcessor, PreProcessor, ProcessorChain

config = initialize_config(sys.modules[__name__])
package_config = config.package_config
log_msg = config.log_message

# Package config
decision_table_path = package_config.get('preparation_editor_input', {}).get('PREPARATION_EDITOR_DECISION_INPUT_PATH', '')
decision_table_file = package_config.get('preparation_editor_input', {}).get('PREPARATION_EDITOR_DECISION_INPUT_PICKLE', '')
integrated_request_list_table_path = package_config.get('preparation_editor_input', {}).get('PREPARATION_EDITOR_INTEGRATED_INPUT_PATH', '')
integrated_request_list_table_file = package_config.get('preparation_editor_input', {}).get('PREPARATION_EDITOR_INTEGRATED_INPUT_PICKLE', '')
preparation_edited = package_config.get('preparation_editor_output', {}).get('PREPARATION_EDITOR_OUTPUT_PICKLE', '')
reference_table = package_config.get('reference_table', {}).get('REFERENCE_TABLE_PICKLE', '')
debug_preedit_result_xlsx = package_config.get('preparation_debug', {}).get('PREEDIT_RESULT_EXCEL_FILE', '')
debug_merge_result_xlsx = package_config.get('preparation_debug', {}).get('MERGE_RESULT_EXCEL_FILE', '')
debug_preparation_editor_result_xlsx = package_config.get('preparation_debug', {}).get('PREPARATION_EDITOR_RESULT_EXCEL_FILE', '')

# Decision table mapping
decision_table_columns_def = package_config.get('decision_table_layout', {}).get('DECISION_TABLE_COLUMNS', '')
columns_to_transform_def = package_config.get('decision_table_layout', {}).get('COLUMNS_TO_TRANSFORM', '')
decision_table_columns_fin_def = package_config.get('decision_table_layout', {}).get('DECISION_TABLE_COLUMNS_FIN', '')

class PreparationChainProcessorError(Exception):
    pass

class PreProcessorDecisionTable(PreProcessor):
    def chain_pre_processor(self) -> list[PreProcessor]:
        return [
            ReadDecisionTable(),
            ModifyDecisionTable(),
        ]

class PreProcessorMerge(PreProcessor):
    def chain_pre_processor(self) -> list[PreProcessor]:
        return [ 
            ReadIntegratedRequestListTable(),
            AddDecisionJudgeColumns(),
            PreMergeDataEditor(),
            ReferenceDataMerger(),
            BPRADFlagInitializer(),
            LoookupReferenceData(),
        ]

class PostProcessor(PostProcessor):
    def chain_post_processor(self) -> list[PostProcessor]:
        return [
            WritePreparationResult(),
        ]

class ReadDecisionTable(PreProcessor):
    def process(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()
        try:
            decision = TableSearcher(decision_table_file, decision_table_path)
        except Exception as e:
            err_msg = f'DecisionTable読み込みで失敗が発生しました: {str(e)}'
            raise PreparationChainProcessorError(err_msg) from None
        else:
            return decision.df.fillna('')

class ModifyDecisionTable(PreProcessor):
    def process(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()
        df.columns = decision_table_columns_def
        for col in columns_to_transform_def:
            df[col] = self._replace_values(df[col])
        return df.loc[:, decision_table_columns_fin_def].fillna('')

    def _replace_values(self, column):
        column = column.replace('4桁', 'is_4digits')
        column = column.replace('5桁', 'is_5digits')
        column = column.replace('なし', 'is_empty')
        column = column.replace('あり', 'is_not_empty')
        column = column.replace(r'^-$', 'any', regex=True)
        return column

class ReadIntegratedRequestListTable(PreProcessor):
    def process(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()
        try:
            integrated_request_list_table = TableSearcher(integrated_request_list_table_file)
        except Exception as e:
            err_msg = f'受付処理一括申請ファイル読み込みで失敗が発生しました: {str(e)}'
            raise PreparationChainProcessorError(err_msg) from None
        else:
            return integrated_request_list_table.df.fillna('')

class AddDecisionJudgeColumns(PreProcessor):
    def process(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()
        return self._add_decision_table_columns(df).fillna('')

    def _add_decision_table_columns(self, df):
        df['branch_code'] = df['branch_code'].astype(str)
        df['branch_code_digit'] = df['branch_code']
        df['branch_code_first_digit'] = df['branch_code'].astype(str).str[0]
        df['branch_code_4_digits_application_status'] = df.apply(
            lambda row: 'exist' if not df[
                (df['branch_code'].str.match(r'^\d{4}$')) &
                (df['branch_code'].str[:4] == row['branch_code'][:4]) &
                ((df['application_type'] == ApplicationType.NEW.value) |
                 (df['application_type'] == ApplicationType.MODIFY.value)) &
                (df['target_org'] == OrganizationType.BRANCH.value)
            ].empty else '', axis=1
        )
        return df.fillna('')

class PreMergeDataEditor(PreProcessor):
    def process(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()
        df = PreparationPreMapping.setup_section_under_internal_sales_integrated_data(df)
        df = PreparationPreMapping.setup_internal_sales_to_integrated_data(df)
        df = PreparationPreMapping.setup_area_to_integrated_data(df)
        try:
            df.to_excel(debug_preedit_result_xlsx, index=None)
        except Exception as e:
            err_msg = f'受付処理マージ処理結果デバッグ用ファイル書き込みで失敗が発生しました ただし処理は継続します: {str(e)}'
            log_msg(f'{err_msg}', LogLevel.INFO)
        return df.fillna('')

class ReferenceDataMerger(PreProcessor):
    def process(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()
        df = ReferenceMergers.merge_zero_group_parent_branch_with_self(df)
        reference = TableSearcher(reference_table)
        df = ReferenceMergers.merge_zero_group_parent_branch_with_reference(df, reference.df)
        df = ReferenceMergers.match_unique_reference(df, reference.df)
        return df.fillna('')

class BPRADFlagInitializer(PreProcessor):
    def process(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()
        bpr_ad = BprAdFlagDeterminer(df)
        df['bpr_target_flag'] = df.apply(bpr_ad.determine_bpr_ad_flag, axis=1)
        try:
            df.to_excel(debug_merge_result_xlsx, index=None)
        except Exception as e:
            err_msg = f'受付処理マージ処理結果デバッグ用ファイル書き込みで失敗が発生しました、ただし処理は継続します: {str(e)}'
            log_msg(f'{err_msg}', LogLevel.INFO)
        return df.fillna('')

class LoookupReferenceData(PreProcessor):
    def process(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()
        log_msg('申請明細.申請区分とリファレンス明細存在整合性チェック:', LogLevel.INFO)
        mask_new_error = (df['application_type'] == ApplicationType.NEW.value) & (df['reference_branch_code_bpr'] != "")
        mask_custom_error = (df['application_type'] != ApplicationType.NEW.value) & (df['reference_branch_code_bpr'] == "")
        if sum(mask_new_error):
            err_msg = f'新設申請だが対となる明細がリファレンス上に存在しています: {sum(mask_new_error)}'
            log_msg(err_msg, LogLevel.ERROR)
            tabulate_dataframe(df[mask_new_error])
        if sum(mask_custom_error):
            err_msg = f'変更・削除申請だが対となる明細がリファレンス上に存在しません: {sum(mask_custom_error)}'
            log_msg(err_msg, LogLevel.ERROR)
            tabulate_dataframe(df[mask_custom_error])
        return df.fillna('')

class WritePreparationResult(PostProcessor):
    def process(self, df: pd.DataFrame) -> None:
        df = df.copy()
        try:
            df.to_pickle(preparation_edited)
            df = df.astype(str)
            df.to_excel(debug_preparation_editor_result_xlsx, index=None)
        except Exception as e:
            err_msg = f'受付処理結果ファイル書き込みで失敗が発生しました: {str(e)}'
            raise PreparationChainProcessorError(err_msg) from None
