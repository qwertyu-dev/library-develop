import pandas as pd
import ulid

class ExcelProcessorError(Exception):
    """Base exception for ExcelProcessor errors"""

class InvalidFileError(ExcelProcessorError):
    """Raised when the file is invalid or cannot be read"""

class InvalidDataError(ExcelProcessorError):
    """Raised when the data in the Excel file is invalid"""

class ExcelProcessor:
    """Excel処理の基底クラス

    Class Overview:
        このクラスはExcelファイルの読み込み、データの検証、
        統一レイアウトへのマッピングを行う基本機能を提供します。

    Methods:
        read_and_map(file_path): Excelファイルを読み込み、列名をマッピングします
        validate_data(df): データフレームの内容を検証します
        map_to_unified_layout(df): データを統一レイアウトにマッピングします
        process(file_path): ファイルの読み込みから統一レイアウトへの変換までの全処理を行います

    Usage Example:
        >>> processor = ExcelProcessor()
        >>> result_df = processor.process("path/to/excel_file.xlsx")

    Notes:
        - このクラスは抽象基底クラスとして機能し、具体的な実装はサブクラスで行います

    Dependency:
        - pandas
        - ulid

    ResourceLocation:
        - [本体]
            - /path/to/excel_processor.py
        - [テストコード]
            - /path/to/test_excel_processor.py

    Todo:
        - ExcelファイルPathに含まれるキーワードにより呼び出し分類をするがprocessで引数渡しよりもインスタンス生成時に渡すべきかの再考

    Change History:
    | No   | 修正理由     | 修正点   | 対応日     | 担当 |
    |------|--------------|----------|-    -------|------|
    | v0.1 | 初期定義作成 | 新規作成 | 2024/07/20 |      |

    """
    def __init__(self) -> None:
        """統合レイアウトをインスタンス共有します

        Arguments:
        なし

        Return Value:
        なし

        Exceptions:
        なし
        """
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
            'auth_transfer_date',
            'sales_department_code_within_location',
            'sales_department_name_within_location',
            'area_code',
            'area_name',
            'remarks',
            'branch_name_kana',
            'section_gr_name_kana',
            'section_gr_name_abbr',
            'bpr_target_flag',
        ]

    def read_and_map(self, file_path: str) -> pd.DataFrame:  # noqa: ARG002 interface定義上の引数定義でありinterface上で使用されないため
        """Excelファイルを読み込み、列名をマッピングします

        Arguments:
        file_path (str): 読み込むExcelファイルのパス

        Return Value:
        pd.DataFrame: マッピング後のデータフレーム

        Exceptions:
        NotImplementedError: このメソッドはサブクラスで実装する必要があります
        """
        err_msg = "Subclasses must implement read_and_map method"
        raise NotImplementedError(err_msg)

    def map_to_unified_layout(self, df: pd.DataFrame) -> pd.DataFrame: # noqa: ARG002 interface定義上の引数定義
        """データを統一レイアウトにマッピングします

        Arguments:
        df (pd.DataFrame): マッピング対象のデータフレーム

        Return Value:
        pd.DataFrame: 統一レイアウトに変換されたデータフレーム

        Exceptions:
        NotImplementedError: このメソッドはサブクラスで実装する必要があります
        """
        err_msg = "Subclasses must implement map_to_unified_layout method"
        raise NotImplementedError(err_msg)

    def validate_data(self, df: pd.DataFrame) -> None: # noqa: ARG002 interface定義上の引数定義
        """データフレームの内容を検証します

        Arguments:
        df (pd.DataFrame): 検証対象のデータフレーム

        Exceptions:
        NotImplementedError: このメソッドはサブクラスで実装する必要があります
        """
        err_msg = "Subclasses must implement validate_data method"
        raise NotImplementedError(err_msg)

    def process(self, file_path: str) -> pd.DataFrame:
        """ファイルの読み込みから統一レイアウトへの変換までの全処理を行います

        Arguments:
        file_path (str): 処理対象のExcelファイルのパス

        Return Value:
        pd.DataFrame: 統一レイアウトに変換されたデータフレーム

        Exceptions:
        ExcelProcessorError: 処理中に予期しないエラーが発生した場合

        Algorithm:
            1. ファイルを読み込み、列名をマッピング
            2. データの検証
            3. 統一レイアウトへの変換
        """
        try:
            _df = self.read_and_map(file_path)
            self.validate_data(_df)
            return self.map_to_unified_layout(_df)
        except ExcelProcessorError:
            raise
        except Exception as e:
            err_msg = f"Unexpected error occurred: {str(e)}"
            raise ExcelProcessorError(err_msg) from None


class JinjiExcelProcessor(ExcelProcessor):
    """人事部門用Excelファイル処理クラス

    Class Overview:
        このクラスは人事部門のExcelファイルを読み込み、
        データを検証し、統一レイアウトに変換します。

    Attributes:
        column_mapping (dict): Excelファイルの列名と内部使用の列名のマッピング

    Methods:
        read_and_map(file_path): 人事部門のExcelファイルを読み込み、列名をマッピング
        validate_data(df): 人事データの検証
        map_to_unified_layout(df): 人事データを統一レイアウトに変換

    Usage Example:
        >>> processor = JinjiExcelProcessor()
        >>> result_df = processor.process("path/to/jinji_excel_file.xlsx")

    Notes:
        - このクラスは人事部門特有のデータ形式に対応しています

    Dependency:
        - pandas
        - ulid

    ResourceLocation:
        - [本体]
            - /path/to/jinji_excel_processor.py
        - [テストコード]
            - /path/to/test_jinji_excel_processor.py

    Change History:
    | No | 修正理由 | 修正点 | 対応日 | 担当 |
    |----|----------|--------|--------|------|
    | v0.1 | 初期定義作成 | 新規作成 | 2024/07/20 | John Doe |

    """

    def read_and_map(self, file_path: str) -> pd.DataFrame:
        """人事部門のExcelファイルを読み込み、列名をマッピングします

        Arguments:
        file_path (str): 読み込むExcelファイルのパス

        Return Value:
        pd.DataFrame: マッピング後のデータフレーム

        Exceptions:
        InvalidFileError: ファイルの読み込みに失敗した場合
        InvalidDataError: 必要な列が存在しない場合

        Algorithm:
            1. Excelファイルを読み込む
            2. 列名のマッピングを適用
            3. 必要な列の存在を確認
        """
        try:
            _df = pd.read_excel(file_path)
        except Exception as e:
            err_msg = f"Failed to read Excel file: {str(e)}"
            raise InvalidFileError(err_msg) from None

        column_mapping: dict[str, str] = {
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

        if not all(col in _df.columns for col in column_mapping):
            err_msg = "Excel file does not contain all required columns"
            raise InvalidDataError(err_msg) from None

        return _df.rename(columns=column_mapping)

    def validate_data(self, df: pd.DataFrame) -> None:
        """人事データの検証を行います

        Arguments:
        df (pd.DataFrame): 検証対象のデータフレーム

        Exceptions:
        InvalidDataError: 必須項目に空値が含まれる場合

        Algorithm:
            1. 必須列のリストを定義
            2. 各必須列に対して空値チェックを実行
        """
        required_columns = ['application_type', 'target_org', 'branch_code', 'branch_name']
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            raise InvalidDataError(f"Missing required columns: {', '.join(missing_columns)}")

        for col in required_columns:
            if df[col].isna().any():
                err_msg = f"Column '{col}' contains null values"
                raise InvalidDataError(err_msg) from None

    def map_to_unified_layout(self, df: pd.DataFrame) -> pd.DataFrame:
        """人事データを統一レイアウトに変換します

        Arguments:
        df (pd.DataFrame): 変換対象のデータフレーム

        Return Value:
        pd.DataFrame: 統一レイアウトに変換されたデータフレーム

        Exceptions:
        ExcelProcessorError: 変換処理中にエラーが発生した場合

        Algorithm:
            1. 統一レイアウトの列を定義
            2. 新しいデータフレームを作成
            3. 各列のデータをマッピング
            4. ULIDを生成して追加
        """
        try:
            unified_df = pd.DataFrame(columns=self.unified_layout)

            unified_df['ulid'] = [str(ulid.new()) for _ in range(len(df))]
            unified_df['applicant_info'] = '1'
            unified_df['application_type'] = df['application_type']
            unified_df['target_org'] = df['target_org']
            unified_df['business_unit_code'] = df['business_unit_code']
            unified_df['parent_branch_code'] = df['parent_branch_code']
            unified_df['branch_code'] = df['branch_code']
            unified_df['branch_name'] = df['branch_name']
            unified_df['section_gr_code'] = df.apply(lambda row: row['section_area_code'] if row['target_org'] == '課' else '', axis=1)
            unified_df['section_gr_name'] = df.apply(lambda row: row['section_area_name'] if row['target_org'] == '課' else '', axis=1)
            unified_df['section_name_en'] = df['section_area_name_en']
            unified_df['resident_branch_code'] = df['resident_branch_code']
            unified_df['resident_branch_name'] = df['resident_branch_name']
            unified_df['aaa_transfer_date'] = df['aaa_transfer_date']
            unified_df['remarks'] = df['remarks']
            unified_df['area_code'] = df.apply(lambda row: row['section_area_code'] if row['target_org'] == 'エリア' else '', axis=1)
            unified_df['area_name'] = df.apply(lambda row: row['section_area_name'] if row['target_org'] == 'エリア' else '', axis=1)

        except Exception as e:
            err_msg = f"Error occurred while mapping to unified layout: {str(e)}"
            raise ExcelProcessorError(err_msg) from None
        else:
            return unified_df[self.unified_layout].fillna("")

class KokukiExcelProcessorWithDummuy(ExcelProcessor):
    """国際事務企画部門用Excelファイル処理クラス

    Class Overview:
        このクラスは国際事務企画部門のExcelファイルを読み込み、
        データを検証し、統一レイアウトに変換します。

    Attributes:
        column_mapping (dict): Excelファイルの列名と内部使用の列名のマッピング

    Methods:
        read_and_map(file_path): 国際事務企画部門のExcelファイルを読み込み、列名をマッピング
        validate_data(df): 国際事務企画データの検証
        map_to_unified_layout(df): 国際事務企画データを統一レイアウトに変換

    Usage Example:
        >>> processor = KokukiExcelProcessor()
        >>> result_df = processor.process("path/to/kokuki_excel_file.xlsx")

    Notes:
        - このクラスは国際事務企画部門特有のデータ形式に対応しています

    Dependency:
        - pandas
        - ulid

    ResourceLocation:
        - [本体]
            - /path/to/kokuki_excel_processor.py
        - [テストコード]
            - /path/to/test_kokuki_excel_processor.py

    Change History:
    | No | 修正理由 | 修正点 | 対応日 | 担当 |
    |----|----------|--------|--------|------|
    | v0.1 | 初期定義作成 | 新規作成 | 2024/07/20 | John Doe |

    """

    def read_and_map(self, file_path: str) -> pd.DataFrame:
        """国際事務企画部門のExcelファイルを読み込み、列名をマッピングします

        Arguments:
        file_path (str): 読み込むExcelファイルのパス

        Return Value:
        pd.DataFrame: マッピング後のデータフレーム

        Exceptions:
        InvalidFileError: ファイルの読み込みに失敗した場合
        InvalidDataError: 必要な列が存在しない場合

        Algorithm:
            1. Excelファイルを読み込む
            2. 列名のマッピングを適用
            3. 必要な列の存在を確認
        """
        try:
            _df = pd.read_excel(file_path)
        except Exception as e:
            err_msg = f"Failed to read Excel file: {str(e)}"
            raise InvalidFileError(err_msg) from None

        column_mapping = {
            '報告日': 'report_date',
            'no': 'application_number',
            '登録予定日(yyyy/mm/dd)': 'effective_date',
            '種類(新規変更廃止)': 'application_type',
            '対象(課・エリア/中間階層)': 'target_org',
            '部店店番': 'branch_code',
            '部店名称:日本語': 'branch_name_ja',
            '部店名称:英語': 'branch_name_en',
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
        if not all(col in _df.columns for col in column_mapping):
            err_msg = "Excel file does not contain all required columns"
            raise InvalidDataError(err_msg) from None

        return _df.rename(columns=column_mapping)

    def validate_data(self, df: pd.DataFrame) -> None:
        """国際事務企画データの検証を行います

        Arguments:
        df (pd.DataFrame): 検証対象のデータフレーム

        Exceptions:
        InvalidDataError: 必須項目に空値が含まれる場合

        Algorithm:
            1. 必須列のリストを定義
            2. 各必須列に対して空値チェックを実行
        """
        required_columns = ['application_type', 'target_org', 'branch_code', 'branch_name_ja']
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            raise InvalidDataError(f"Missing required columns: {', '.join(missing_columns)}")

        for col in required_columns:
            if df[col].isna().any():
                err_msg = f"Column '{col}' contains null values"
                raise InvalidDataError(err_msg) from None

    def map_to_unified_layout(self, df: pd.DataFrame) -> pd.DataFrame:
        """国際事務企画データを統一レイアウトに変換します

        Arguments:
        df (pd.DataFrame): 変換対象のデータフレーム

        Return Value:
        pd.DataFrame: 統一レイアウトに変換されたデータフレーム

        Exceptions:
        ExcelProcessorError: 変換処理中にエラーが発生した場合

        Algorithm:
            1. 統一レイアウトの列を定義
            2. 新しいデータフレームを作成
            3. 各列のデータをマッピング
            4. ULIDを生成して追加
            5. エリア情報の条件付きマッピング
        """
        try:
            unified_df = pd.DataFrame(columns=self.unified_layout)

            unified_df['ulid'] = [str(ulid.new()) for _ in range(len(df))]
            unified_df['applicant_info'] = '2'
            unified_df['application_type'] = df['application_type']
            unified_df['target_org'] = df['target_org']
            unified_df['branch_code'] = df['branch_code']
            unified_df['branch_name'] = df['branch_name_ja']
            unified_df['section_gr_code'] = df['section_area_code']
            unified_df['section_gr_name'] = df['section_area_name_ja']
            unified_df['section_name_en'] = df['section_area_name_en']
            unified_df['aaa_transfer_date'] = df['aaa_transfer_date']
            unified_df['section_gr_name_abbr'] = df['section_area_abbr_ja']

        except Exception as e:
            err_msg = f"Error occurred while mapping to unified layout: {str(e)}"
            raise ExcelProcessorError(err_msg) from None
        else:
            return unified_df[self.unified_layout].fillna("")

class KanrenExcelProcessorWithDummy(ExcelProcessor):
    """関連会社用Excelファイル処理クラス

    Class Overview:
        このクラスは関連会社のExcelファイルを読み込み、
        データを検証し、統一レイアウトに変換します。

    Attributes:
        column_mapping (dict): Excelファイルの列名と内部使用の列名のマッピング

    Methods:
        read_and_map(file_path): 関連会社のExcelファイルを読み込み、列名をマッピング
        validate_data(df): 関連会社データの検証
        map_to_unified_layout(df): 関連会社データを統一レイアウトに変換

    Usage Example:
        >>> processor = KanrenExcelProcessor()
        >>> result_df = processor.process("path/to/kanren_excel_file.xlsx")

    Notes:
        - このクラスは関連会社特有のデータ形式に対応しています

    Dependency:
        - pandas
        - ulid

    ResourceLocation:
        - [本体]
            - /path/to/kanren_excel_processor.py
        - [テストコード]
            - /path/to/test_kanren_excel_processor.py

    Change History:
    | No | 修正理由 | 修正点 | 対応日 | 担当 |
    |----|----------|--------|--------|------|
    | v0.1 | 初期定義作成 | 新規作成 | 2024/07/20 | John Doe |

    """

    def read_and_map(self, file_path: str) -> pd.DataFrame:
        """関連会社のExcelファイルを読み込み、列名をマッピングします

        Arguments:
        file_path (str): 読み込むExcelファイルのパス

        Return Value:
        pd.DataFrame: マッピング後のデータフレーム

        Exceptions:
        InvalidFileError: ファイルの読み込みに失敗した場合
        InvalidDataError: 必要な列が存在しない場合

        Algorithm:
            1. Excelファイルを読み込む
            2. 列名のマッピングを適用
            3. 必要な列の存在を確認
        """
        try:
            _df = pd.read_excel(file_path)
        except Exception as e:
            err_msg = f"Failed to read Excel file: {str(e)}"
            raise InvalidFileError(err_msg) from None

        column_mapping = {
            '種類': 'application_type',
            '部門コード': 'business_unit_code',
            '対象': 'target_org',
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
        if not all(col in _df.columns for col in column_mapping):
            err_msg = "Excel file does not contain all required columns"
            raise InvalidDataError(err_msg) from None

        return _df.rename(columns=column_mapping)

    def validate_data(self, df: pd.DataFrame) -> None:
        """関連会社データの検証を行います

        Arguments:
        df (pd.DataFrame): 検証対象のデータフレーム

        Exceptions:
        InvalidDataError: 必須項目に空値が含まれる場合

        Algorithm:
            1. 必須列のリストを定義
            2. 各必須列に対して空値チェックを実行
        """
        required_columns = ['application_type', 'branch_code', 'branch_name']
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            raise InvalidDataError(f"Missing required columns: {', '.join(missing_columns)}")
        for col in required_columns:
            if df[col].isna().any():
                err_msg = f"Column '{col}' contains null values"
                raise InvalidDataError(err_msg) from None

    def map_to_unified_layout(self, df: pd.DataFrame) -> pd.DataFrame:
        """関連会社データを統一レイアウトに変換します

        Arguments:
        df (pd.DataFrame): 変換対象のデータフレーム

        Return Value:
        pd.DataFrame: 統一レイアウトに変換されたデータフレーム

        Exceptions:
        ExcelProcessorError: 変換処理中にエラーが発生した場合

        Algorithm:
            1. 統一レイアウトの列を定義
            2. 新しいデータフレームを作成
            3. 各列のデータをマッピング
            4. ULIDを生成して追加
            5. target_orgを条件に基づいて設定
        """
        try:
            unified_df = pd.DataFrame(columns=self.unified_layout)

            unified_df['ulid'] = [str(ulid.new()) for _ in range(len(df))]
            unified_df['applicant_info'] = '3'  # ダミー課あり 
            unified_df['application_type'] = df['application_type']
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

        except Exception as e:
            err_msg = f"Error occurred while mapping to unified layout: {str(e)}"
            raise ExcelProcessorError(err_msg) from None
        else:
            return unified_df[self.unified_layout].fillna("")

class KanrenExcelProcessorWithoutDummy(ExcelProcessor):
    """関連会社用Excelファイル処理クラス

    Class Overview:
        このクラスは関連会社のExcelファイルを読み込み、
        データを検証し、統一レイアウトに変換します。

    Attributes:
        column_mapping (dict): Excelファイルの列名と内部使用の列名のマッピング

    Methods:
        read_and_map(file_path): 関連会社のExcelファイルを読み込み、列名をマッピング
        validate_data(df): 関連会社データの検証
        map_to_unified_layout(df): 関連会社データを統一レイアウトに変換

    Usage Example:
        >>> processor = KanrenExcelProcessor()
        >>> result_df = processor.process("path/to/kanren_excel_file.xlsx")

    Notes:
        - このクラスは関連会社特有のデータ形式に対応しています

    Dependency:
        - pandas
        - ulid

    ResourceLocation:
        - [本体]
            - /path/to/kanren_excel_processor.py
        - [テストコード]
            - /path/to/test_kanren_excel_processor.py

    Change History:
    | No | 修正理由 | 修正点 | 対応日 | 担当 |
    |----|----------|--------|--------|------|
    | v0.1 | 初期定義作成 | 新規作成 | 2024/07/20 | John Doe |

    """

    def read_and_map(self, file_path: str) -> pd.DataFrame:
        """関連会社のExcelファイルを読み込み、列名をマッピングします

        Arguments:
        file_path (str): 読み込むExcelファイルのパス

        Return Value:
        pd.DataFrame: マッピング後のデータフレーム

        Exceptions:
        InvalidFileError: ファイルの読み込みに失敗した場合
        InvalidDataError: 必要な列が存在しない場合

        Algorithm:
            1. Excelファイルを読み込む
            2. 列名のマッピングを適用
            3. 必要な列の存在を確認
        """
        try:
            _df = pd.read_excel(file_path)
        except Exception as e:
            err_msg = f"Failed to read Excel file: {str(e)}"
            raise InvalidFileError(err_msg) from None

        column_mapping = {
            '種類': 'application_type',
            '部門コード': 'business_unit_code',
            '対象': 'target_org',
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
        if not all(col in _df.columns for col in column_mapping):
            err_msg = "Excel file does not contain all required columns"
            raise InvalidDataError(err_msg) from None

        return _df.rename(columns=column_mapping)

    def validate_data(self, df: pd.DataFrame) -> None:
        """関連会社データの検証を行います

        Arguments:
        df (pd.DataFrame): 検証対象のデータフレーム

        Exceptions:
        InvalidDataError: 必須項目に空値が含まれる場合

        Algorithm:
            1. 必須列のリストを定義
            2. 各必須列に対して空値チェックを実行
        """
        required_columns = ['application_type', 'branch_code', 'branch_name']
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            raise InvalidDataError(f"Missing required columns: {', '.join(missing_columns)}")
        for col in required_columns:
            if df[col].isna().any():
                err_msg = f"Column '{col}' contains null values"
                raise InvalidDataError(err_msg) from None

    def map_to_unified_layout(self, df: pd.DataFrame) -> pd.DataFrame:
        """関連会社データを統一レイアウトに変換します

        Arguments:
        df (pd.DataFrame): 変換対象のデータフレーム

        Return Value:
        pd.DataFrame: 統一レイアウトに変換されたデータフレーム

        Exceptions:
        ExcelProcessorError: 変換処理中にエラーが発生した場合

        Algorithm:
            1. 統一レイアウトの列を定義
            2. 新しいデータフレームを作成
            3. 各列のデータをマッピング
            4. ULIDを生成して追加
            5. target_orgを条件に基づいて設定
        """
        try:
            unified_df = pd.DataFrame(columns=self.unified_layout)

            unified_df['ulid'] = [str(ulid.new()) for _ in range(len(df))]
            unified_df['applicant_info'] = '4'  # ダミー課なし 
            unified_df['application_type'] = df['application_type']
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

        except Exception as e:
            err_msg = f"Error occurred while mapping to unified layout: {str(e)}"
            raise ExcelProcessorError(err_msg) from None
        else:
            return unified_df[self.unified_layout].fillna("")
