import pandas as pd
import ulid

class ExcelProcessor:
    def read_and_map(self, file_path: str) -> pd.DataFrame:
        raise NotImplementedError("Subclasses must implement read_and_map method")

    def map_to_unified_layout(self, df: pd.DataFrame) -> pd.DataFrame:
        raise NotImplementedError("Subclasses must implement map_to_unified_layout method")

class JinjiExcelProcessor(ExcelProcessor):
    def read_and_map(self, file_path: str) -> pd.DataFrame:
        df = pd.read_excel(file_path)
        column_mapping = {
            '報告日': 'report_date',
            'no': 'application_number',
            '有効日付': 'effective_date',
            '種類': 'application_type',
            '対象': 'target_org',
            '部門コード': 'business_unit_code',
            '親部店コード': 'parent_branch_code',
            '部店コード': 'branch_code',
            '部店名称': 'branch_name',
            '部店名称(英語)': 'branch_name_en',
            '課/エリアコード': 'section_area_code',
            '課/エリア名称': 'section_area_name',
            '課/エリア名称(英語)': 'section_area_name_en',
            '常駐部店コード': 'resident_branch_code',
            '常駐部店名称': 'resident_branch_name',
            '純新規店の組織情報受渡し予定日(開店日基準)': 'new_org_info_transfer_date',
            '共通認証受渡し予定日(人事データ反映基準)': 'aaa_transfer_date',
            '備考': 'remarks',
        }
        return df.rename(columns=column_mapping)

    def map_to_unified_layout(self, df: pd.DataFrame) -> pd.DataFrame:
        unified_layout = [
            'ulid',
            'applicant_info',
            'application_type',
            'target_org',
            'business_unit_code',
            'parent_branch_code',
            'branch_code',
            'branch_name',
            'section_gr_code',
            'section_gr_name',
            'section_name_en',
            'resident_branch_code',
            'resident_branch_name',
            'auth_transfer_date',
            'sales_department_code_within_loc',
            'sales_department_name_within_loc',
            'area_code',
            'area_name',
            'remarks',
            'branch_name_kana',
            'section_gr_name_kana',
            'section_gr_name_abbr',
            'bpr_target_flag',
        ]

        unified_df = pd.DataFrame(columns=unified_layout)

        unified_df['ulid'] = [str(ulid.new()) for _ in range(len(df))]
        unified_df['applicant_info'] = '1'
        unified_df['application_type'] = df['application_type']
        unified_df['target_org'] = df['target_org']
        unified_df['business_unit_code'] = df['business_unit_code']
        unified_df['parent_branch_code'] = df['parent_branch_code']
        unified_df['branch_code'] = df['branch_code']
        unified_df['branch_name'] = df['branch_name']
        unified_df['section_gr_code'] = df['section_area_code']
        unified_df['section_gr_name'] = df['section_area_name']
        unified_df['section_name_en'] = df['section_area_name_en']
        unified_df['resident_branch_code'] = df['resident_branch_code']
        unified_df['resident_branch_name'] = df['resident_branch_name']
        unified_df['aaa_transfer_date'] = df['aaa_transfer_date']
        unified_df['remarks'] = df['remarks']

        return unified_df

class KokugiExcelProcessor(ExcelProcessor):
    def read_and_map(self, file_path: str) -> pd.DataFrame:
        df = pd.read_excel(file_path)
        column_mapping = {
            '報告日': 'report_date',
            'no': 'application_number',
            '登録予定日(yyyy/mm/dd)': 'effective_date',
            '種類(新規変更廃止)': 'application_type',
            '対象(課・エリア/中間階層)': 'target_org',
            '部店店番': 'branch_code',
            '部店名称 日本語': 'branch_name_ja',
            '部店名称 英語': 'branch_name_en',
            '中間階層コード': 'intermediate_level_code',
            '中間階層名称:日本語': 'intermediate_level_name_ja',
            '中間階層名称:英語': 'intermediate_level_name_en',
            '中間階層略称:日本語': 'intermediate_level_abbr_ja',
            '中間階層略称:英語': 'intermediate_level_abbr_en',
            '課・エリアコード': 'section_area_code',
            '課・エリア名称:日本語': 'section_area_name_ja',
            '課・エリア名称:英語': 'section_area_name_en',
            '課・エリア略称:日本語': 'section_area_abbr_ja',
            '課・エリア略称:英語': 'section_area_abbr_en',
            '共通認証受渡予定日': 'aaa_transfer_date',
            '変更種別・詳細旧名称・略語': 'change_details',
        }
        return df.rename(columns=column_mapping)

    def map_to_unified_layout(self, df: pd.DataFrame) -> pd.DataFrame:
        unified_layout = [
            'ulid',
            'applicant_info',
            'application_type',
            'target_org',
            'business_unit_code',
            'parent_branch_code',
            'branch_code',
            'branch_name',
            'section_gr_code',
            'section_gr_name',
            'section_name_en',
            'resident_branch_code',
            'resident_branch_name',
            'auth_transfer_date',
            'sales_department_code_within_loc',
            'sales_department_name_within_loc',
            'area_code',
            'area_name',
            'remarks',
            'branch_name_kana',
            'section_gr_name_kana',
            'section_gr_name_abbr',
            'bpr_target_flag',
        ]

        unified_df = pd.DataFrame(columns=unified_layout)

        unified_df['ulid'] = [str(ulid.new()) for _ in range(len(df))]
        unified_df['applicant_info'] = '2'
        unified_df['application_type'] = df['application_type']
        unified_df['target_org'] = df['target_org']
        unified_df['branch_code'] = df['branch_code']
        unified_df['branch_name'] = df['branch_name_ja']
        unified_df['section_gr_code'] = df['section_area_code']
        unified_df['section_gr_name'] = df['section_area_name_ja']
        unified_df['section_name_en'] = df['section_area_name_en']
        unified_df['auth_transfer_date'] = df['aaa_transfer_date']
        unified_df['section_gr_name_abbr'] = df['section_area_abbr_ja']
        unified_df['area_code'] = df.apply(lambda row: row['section_area_code'] if row['target_org'] == 'エリア' else '', axis=1)
        unified_df['area_name'] = df.apply(lambda row: row['section_area_name_ja'] if row['target_org'] == 'エリア' else '', axis=1)

        return unified_df

class KanrenExcelProcessor(ExcelProcessor):
    def read_and_map(self, file_path: str) -> pd.DataFrame:
        df = pd.read_excel(file_path)
        column_mapping = {
            '種類': 'application_type',
            '部門コード': 'business_unit_code',
            '親部店コード': 'parent_branch_code',
            '部店コード': 'branch_code',
            '部店名称': 'branch_name',
            '課Grコード': 'section_gr_code',
            '課Gr名称': 'section_gr_name',
            '課名称(英語)': 'section_name_en',
            '共通認証受渡し予定日': 'aaa_transfer_date',
            '部店カナ': 'branch_name_kana',
            '課Gr名称(カナ)': 'section_gr_name_kana',
            '課Gr名称(略称)': 'section_gr_name_abbr',
            'BPR対象/対象外フラグ': 'bpr_target_flag',
        }
        return df.rename(columns=column_mapping)

    def map_to_unified_layout(self, df: pd.DataFrame) -> pd.DataFrame:
        unified_layout = [
            'ulid',
            'applicant_info',
            'application_type',
            'target_org',
            'business_unit_code',
            'parent_branch_code',
            'branch_code',
            'branch_name',
            'section_gr_code',
            'section_gr_name',
            'section_name_en',
            'resident_branch_code',
            'resident_branch_name',
            'auth_transfer_date',
            'sales_department_code_within_loc',
            'sales_department_name_within_loc',
            'area_code',
            'area_name',
            'remarks',
            'branch_name_kana',
            'section_gr_name_kana',
            'section_gr_name_abbr',
            'bpr_target_flag',
        ]

        unified_df = pd.DataFrame(columns=unified_layout)

        unified_df['ulid'] = [str(ulid.new()) for _ in range(len(df))]
        unified_df['applicant_info'] = '3'  # または '4' (条件に応じて設定が必要)
        unified_df['application_type'] = df['application_type']
        unified_df['target_org'] = df.apply(lambda row: '課' if row['section_gr_code'] else '部店', axis=1)
        unified_df['business_unit_code'] = df['business_unit_code']
        unified_df['parent_branch_code'] = df['parent_branch_code']
        unified_df['branch_code'] = df['branch_code']
        unified_df['branch_name'] = df['branch_name']
        unified_df['section_gr_code'] = df['section_gr_code']
        unified_df['section_gr_name'] = df['section_gr_name']
        unified_df['section_name_en'] = df['section_name_en']
        unified_df['auth_transfer_date'] = df['aaa_transfer_date']
        unified_df['branch_name_kana'] = df['branch_name_kana']
        unified_df['section_gr_name_kana'] = df['section_gr_name_kana']
        unified_df['section_gr_name_abbr'] = df['section_gr_name_abbr']
        unified_df['bpr_target_flag'] = df['bpr_target_flag']

        return unified_df
