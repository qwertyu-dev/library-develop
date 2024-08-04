import pandas as pd
import ulid
from tabulate import tabulate

class ExcelProcessor:
    def __init__(self):
        self.unified_layout = [
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
            'aaa_transfer_date',
            'sales_department_code_within_loc',
            'sales_department_name_within_loc', 'area_code',
            'area_name',
            'remarks',
            'branch_name_kana',
            'section_gr_name_kana',
            'section_gr_name_abbr',
            'bpr_target_flag',
        ]

    def read_and_map(self, file_path: str) -> pd.DataFrame:
        err_msg = "Subclasses must implement read_and_map method"
        raise NotImplementedError(err_msg) from None

    def map_to_unified_layout(self, df: pd.DataFrame) -> pd.DataFrame:
        err_msg = "Subclasses must implement map_to_unified_layout method"
        raise NotImplementedError(err_msg) from None
        

class JinjiExcelProcessor(ExcelProcessor):
    def read_and_map(self, file_path: str) -> pd.DataFrame:
        _df = pd.read_excel(file_path)
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
        return _df.rename(columns=column_mapping)

    def map_to_unified_layout(self, df: pd.DataFrame) -> pd.DataFrame:
        # 一律適用
        unified_df = pd.DataFrame(columns=self.unified_layout)

        unified_df['ulid'] = [str(ulid.new()) for _ in range(len(df))]

        unified_df['applicant_info'] = '1'  # 判定関数に置き換え
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

        # 最後にレイアウト順を再保証する
        return unified_df[self.unified_layout].fillna("")

class KokukiExcelProcessor(ExcelProcessor):
    def read_and_map(self, file_path: str) -> pd.DataFrame:
        _df = pd.read_excel(file_path)
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
        return _df.rename(columns=column_mapping)

    def map_to_unified_layout(self, df: pd.DataFrame) -> pd.DataFrame:
        # 一律適用
        unified_df = pd.DataFrame(columns=self.unified_layout)

        unified_df['ulid'] = [str(ulid.new()) for _ in range(len(df))]
        unified_df['applicant_info'] = '2'  # 判定関数へ置き換え
        unified_df['application_type'] = df['application_type']
        unified_df['target_org'] = df['target_org']
        unified_df['branch_code'] = df['branch_code']
        unified_df['branch_name'] = df['branch_name_ja']
        unified_df['section_gr_code'] = df['section_area_code']
        unified_df['section_gr_name'] = df['section_area_name_ja']
        unified_df['section_name_en'] = df['section_area_name_en']
        unified_df['aaa_transfer_date'] = df['aaa_transfer_date']
        unified_df['section_gr_name_abbr'] = df['section_area_abbr_ja']
        unified_df['area_code'] = df.apply(lambda row: row['section_area_code'] if row['target_org'] == 'エリア' else '', axis=1)
        unified_df['area_name'] = df.apply(lambda row: row['section_area_name_ja'] if row['target_org'] == 'エリア' else '', axis=1)

        # 最後にレイアウト順を再保証する
        return unified_df[self.unified_layout].fillna("")

class KanrenExcelProcessor(ExcelProcessor):
    def read_and_map(self, file_path: str) -> pd.DataFrame:
        _df = pd.read_excel(file_path)
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
        return _df.rename(columns=column_mapping)

    def map_to_unified_layout(self, df: pd.DataFrame) -> pd.DataFrame:
        # 一律適用
        unified_df = pd.DataFrame(columns=self.unified_layout)

        unified_df['ulid'] = [str(ulid.new()) for _ in range(len(df))]
        unified_df['applicant_info'] = '3'  # 判定関数へ置き換え
        unified_df['application_type'] = df['application_type']
        unified_df['target_org'] = df.apply(lambda row: '課' if row['section_gr_code'] else '部店', axis=1)  ## 見直し
        unified_df['business_unit_code'] = df['business_unit_code']
        unified_df['parent_branch_code'] = df['parent_branch_code']
        unified_df['branch_code'] = df['branch_code']
        unified_df['branch_name'] = df['branch_name']
        unified_df['section_gr_code'] = df['section_gr_code']
        unified_df['section_gr_name'] = df['section_gr_name']
        unified_df['section_name_en'] = df['section_name_en']
        unified_df['aaa_transfer_date'] = df['aaa_transfer_date']
        unified_df['branch_name_kana'] = df['branch_name_kana']
        unified_df['section_gr_name_kana'] = df['section_gr_name_kana']
        unified_df['section_gr_name_abbr'] = df['section_gr_name_abbr']
        unified_df['bpr_target_flag'] = df['bpr_target_flag']

        # 最後にレイアウト順を再保証する
        return unified_df[self.unified_layout].fillna("")

# サンプルデータの作成と処理
def process_and_print(processor, data, data_path, case_name):
    print(f"\n{case_name} Case:")
    
    # オリジナルデータ
    print("\nOriginal Data:")
    print(tabulate(data, headers='keys', tablefmt='pipe', showindex=False))
    
    # 最初のマッピング（read_and_map の結果）
    df_mapped = processor.read_and_map(data_path)
    print("\nFirst Mapping:")
    print(tabulate(df_mapped, headers='keys', tablefmt='pipe', showindex=False))
    
    # 最後のマッピング（統合レイアウト）
    df_unified = processor.map_to_unified_layout(df_mapped)
    print("\nFinal Unified Layout:")
    print(tabulate(df_unified, headers='keys', tablefmt='pipe', showindex=False))

# 人事のサンプルデータ
jinji_data = pd.DataFrame({
    '報告日': ['2023-05-01', '2023-05-01'],
    'no': [1, 2],
    '有効日付': ['2023-06-01', '2023-06-01'],
    '種類': ['新設', '変更'],
    '対象': ['部', '課'],
    '部門コード': ['A01', 'B02'],
    '親部店コード': ['P001', 'P002'],
    '部店コード': ['S001', 'S002'],
    '部店名称': ['営業第一部', '企画課'],
    '部店名称(英語)': ['Sales Dept. 1', 'Planning Section'],
    '課/エリアコード': ['', 'G001'],
    '課/エリア名称': ['', '企画第一課'],
    '課/エリア名称(英語)': ['', 'Planning Section 1'],
    '常駐部店コード': ['R001', 'R002'],
    '常駐部店名称': ['本店', '支店A'],
    '純新規店の組織情報受渡し予定日(開店日基準)': ['2023-05-25', ''],
    '共通認証受渡し予定日(人事データ反映基準)': ['2023-05-28', '2023-05-28'],
    '備考': ['新設部門', '課名変更'],
})

jinji_data.to_excel('jinji.xlsx')

# 国企のサンプルデータ
kokuki_data = pd.DataFrame({
    '報告日': ['2023-05-01', '2023-05-01', '2023-05-01'],
    'no': [1, 2, 3],
    '登録予定日(yyyy/mm/dd)': ['2023-06-01', '2023-06-01', '2023-06-01'],
    '種類(新規変更廃止)': ['新設', '変更', '新設'],
    '対象(課・エリア/中間階層)': ['課・エリア', '課・エリア', 'エリア'],
    '部店店番': ['S001', 'S002', 'S003'],
    '部店名称 日本語': ['東京支店', '大阪支店', '名古屋エリア'],
    '部店名称 英語': ['Tokyo Branch', 'Osaka Branch', 'Nagoya Area'],
    '課・エリアコード': ['G001', 'G002', 'E001'],
    '課・エリア名称:日本語': ['営業第一課', '営業第二課', '名古屋エリア'],
    '課・エリア名称:英語': ['Sales Section 1', 'Sales Section 2', 'Nagoya Area'],
    '課・エリア略称:日本語': ['営1', '営2', '名古屋'],
    '共通認証受渡予定日': ['2023-05-28', '2023-05-28', '2023-05-28'],
})
kokuki_data.to_excel('kokuki.xlsx')

# 関連のサンプルデータ
kanren_data = pd.DataFrame({
    '種類': ['新設', '変更'],
    '部門コード': ['R01', 'R02'],
    '親部店コード': ['RP001', 'RP002'],
    '部店コード': ['RB001', 'RB002'],
    '部店名称': ['関連会社A', '関連会社B部門'],
    '課Grコード': ['RS001', 'RS002'],
    '課Gr名称': ['営業部', '企画課'],
    '課名称(英語)': ['Sales Department', 'Planning Section'],
    '共通認証受渡し予定日': ['2023-05-28', '2023-05-28'],
    '部店カナ': ['カンレンガイシャA', 'カンレンガイシャBブモン'],
    '課Gr名称(カナ)': ['エイギョウブ', 'キカクカ'],
    '課Gr名称(略称)': ['営', '企'],
    'BPR対象/対象外フラグ': ['1', '1'],
})
kanren_data.to_excel('kanren.xlsx')

# 処理と出力
process_and_print(JinjiExcelProcessor(), jinji_data, "jinji.xlsx", "Jinji")
process_and_print(KokukiExcelProcessor(), kokuki_data, "kokuki.xlsx", "Kokuki")
process_and_print(KanrenExcelProcessor(), kanren_data, "kanren.xlsx", "Kanren")
