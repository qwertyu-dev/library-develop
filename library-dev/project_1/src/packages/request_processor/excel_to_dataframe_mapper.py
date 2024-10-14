import sys

import pandas as pd
import ulid

from src.lib.common_utils.ibr_decorator_config import initialize_config
from src.lib.common_utils.ibr_logger_helper import format_config

# config共有
#from src.lib.common_utils.ibr_decorator_config import with_config
from src.lib.common_utils.ibr_enums import LogLevel

config = initialize_config(sys.modules[__name__])
log_msg = config.log_message

# def. module Exception
class ExcelMappingError(Exception):
    """Base exception for ExcelProcessor errors"""

class InvalidFileError(ExcelMappingError):
    """Raised when the file is invalid or cannot be read"""

class InvalidDataError(ExcelMappingError):
    """Raised when the data in the Excel file is invalid"""

class ExcelMapping:
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
    def __init__(self, conf: dict|None = None) -> None:
        """統合レイアウトをインスタンス共有します

        Arguments:
        なし

        Return Value:
        なし

        Exceptions:
        なし
        """
        # DI
        self.config = conf or config
        self.log_msg = self.config.log_message
        self._column_mapping = None
        self.unified_layout = self.config.package_config.get('layout', []).get('unified_layout', {})
        log_msg(f'\n\nunified_layout: {format_config(self.unified_layout)}', LogLevel.INFO)

    @property
    def column_mappig(self) -> dict:
        if self._column_mapping is None:
            err_msg = 'Subclass Must implement column_mapping'
            raise NotImplementedError(err_msg) from None
        return self._column_mapping

    @column_mappig.setter
    def column_mapping(self, value: dict) -> pd.DataFrame:
        self._column_mapping = value
        log_msg(f'\n\ncolumn_mapping: {format_config(self._column_mapping)}', LogLevel.INFO)

    def column_map(self, df: pd.DataFrame) -> pd.DataFrame:
        _df = df.copy()
        if not all(col in _df.columns for col in self.column_mapping):
            err_msg = "Excel file does not contain all required columns"
            self.log_msg(err_msg, LogLevel.ERROR)
            raise InvalidDataError(err_msg) from None
        return _df.rename(columns=self.column_mapping)

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

class JinjiExcelMapping(ExcelMapping):
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
    def __init__(self, conf: dict | None=None):
        super().__init__(conf)
        self.column_mapping = self.config.package_config['excel_definition_mapping_jinji']

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
            unified_df['business_and_area_code'] = df.apply(lambda row: row['section_area_code'] if row['target_org'] == 'エリア' else '', axis=1)
            unified_df['area_name'] = df.apply(lambda row: row['section_area_name'] if row['target_org'] == 'エリア' else '', axis=1)
            unified_df['remarks'] = df['remarks']
            unified_df['organization_name_kana'] = df['organization_name_kana']

        except Exception as e:
            err_msg = f"Error occurred while mapping to unified layout: {str(e)}"
            self.log_msg(err_msg, LogLevel.ERROR)
            raise ExcelMappingError(err_msg) from None
        else:
            return unified_df[self.unified_layout].fillna("")

class KokukiExcelMapping(ExcelMapping):
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
    def __init__(self, conf: dict|None = None):
        super().__init__(conf)
        self.column_mapping = self.config.package_config['excel_definition_mapping_kokuki']

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
            unified_df['section_gr_code'] = df['section_area_code']
            unified_df['section_gr_name'] = df['section_area_name_ja']
            unified_df['section_name_en'] = df['section_area_name_en']
            unified_df['aaa_transfer_date'] = df['aaa_transfer_date']

        except Exception as e:
            err_msg = f"Error occurred while mapping to unified layout: {str(e)}"
            self.log_msg(err_msg, LogLevel.ERROR)
            raise ExcelMappingError(err_msg) from None
        else:
            return unified_df[self.unified_layout].fillna("")

class KanrenExcelMappingWithDummy(ExcelMapping):
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
    def __init__(self, conf: dict|None = None):
        super().__init__(conf)
        self.column_mapping = self.config.package_config['excel_definition_mapping_kanren']

    def map_to_unified_layout(self, df: pd.DataFrame) -> pd.DataFrame:
        """関連会社データを統一レイアウトに変換します

        ダミー課ありパターン、ただし今後は新規申請は受領しない
        現行ですでにダミー課あり部署のみ変更・削除のメンテナンスを行う

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
            unified_df['section_name_kana'] = df['section_name_kana']
            unified_df['section_name_abbr'] = df['section_name_abbr']
            unified_df['bpr_target_flag'] = df['bpr_target_flag']

        except Exception as e:
            err_msg = f"Error occurred while mapping to unified layout: {str(e)}"
            self.log_msg(err_msg, LogLevel.ERROR)
            raise ExcelMappingError(err_msg) from None
        else:
            return unified_df[self.unified_layout].fillna("")

class KanrenExcelMappingWithoutDummy(ExcelMapping):
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
    def __init__(self, conf: dict|None=None):
        super().__init__(conf)
        self.column_mapping = self.config.package_config['excel_definition_mapping_jinji']

    def map_to_unified_layout(self, df: pd.DataFrame) -> pd.DataFrame:
        """関連会社データを統一レイアウトに変換します

        * ダミー課なしパターン→人事レイアウトで申請する
        * 設定・判定処理は人事と同じとして設定する

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
            unified_df['business_and_area_code'] = df.apply(lambda row: row['section_area_code'] if row['target_org'] == 'エリア' else '', axis=1)
            unified_df['area_name'] = df.apply(lambda row: row['section_area_name'] if row['target_org'] == 'エリア' else '', axis=1)
            unified_df['remarks'] = df['remarks']
            unified_df['organization_name_kana'] = df['organization_name_kana']

        except Exception as e:
            err_msg = f"Error occurred while mapping to unified layout: {str(e)}"
            self.log_msg(err_msg, LogLevel.ERROR)
            raise ExcelMappingError(err_msg) from None
        else:
            return unified_df[self.unified_layout].fillna("")

