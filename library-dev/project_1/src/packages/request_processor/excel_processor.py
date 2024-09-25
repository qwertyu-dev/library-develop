import pandas as pd

from src.lib.common_utils.ibr_enums import LogLevel
from src.lib.common_utils.ibr_dataframe_helper import tabulate_dataframe
from src.lib.common_utils.ibr_excel_reader import ExcelDataLoader

from .file_configuration_factory import FileConfigurationFactory

# config共有
#import sys
from src.lib.common_utils.ibr_decorator_config import with_config
#from src.lib.common_utils.ibr_decorator_config import initialize_config
#config = initialize_config(sys.modules[__name__])

class ExcelProcessorError(Exception):
    pass
def  excel_sheet_columns_unmatch_error():
    """TRY30 ValueError発生させる"""
    raise ValueError

@with_config
class ExcelProcessor:
    """Excelファイルの処理とバリデーションを行うクラス"""

    def __init__(self, config: dict, file_configration_factory: FileConfigurationFactory):
        """ExcelProcessorのコンストラクタ。

        Args:
            file_path (Path): 処理対象のExcelファイルのパス
            sheet_name (str): 処理対象のシート名
            log_msg (Callable): ログメッセージを出力する関数
        """
        # DI config
        self.config = config or self.config
        self.log_msg = self.config.log_message

        # Excel path/sheet fatory
        self.excel_file_pattern = file_configration_factory.create_file_pattern()
        self.log_msg(f"excel file pattern: {self.excel_file_pattern}", LogLevel.DEBUG)

        # Sheet名が固定とは決まっていない可能性がある
        self.excel_sheet_name = file_configration_factory.create_sheet_name()


    def load(self) -> tuple[pd.DataFrame, list[str]]:
        dataframes = []
        common_columns = None

        # 対象全探索
        for file_path in self.excel_file_pattern:
            self.log_msg(f'excel file path: {file_path}', LogLevel.INFO)
            try:
                excel_loader = ExcelDataLoader(file_path)
                _df = excel_loader.read_excel_one_sheet(sheet_name=self.excel_sheet_name)

                # 最初のDataFrameのカラムを共通Columnとし次以降のDataFrameのColumnと一致しない場合はエラーとする
                if common_columns is None:
                    common_columns = list(_df.columns)

                if set(_df.columns) != set(common_columns):
                    # errorはログ出力するが処理は継続
                    err_msg = f'カラム構造が一致しないExcelBookがあります: {file_path}::{self.excel_sheet_name}'
                    excel_sheet_columns_unmatch_error(err_msg) # TRY301 ValueError発生

                # 共通columnsのみを選択しcolumn順序整備
                _df = _df[common_columns]
                # 積み上げ
                dataframes.append(_df)
            except Exception as e:
                raise ExcelProcessorError from e

        if not dataframes:
            return pd.DataFrame(), []

        combined_df = pd.concat(dataframes, ignore_index=True)

        return combined_df, []

    def _log_dataframe_info(self, df: pd.DataFrame) -> None:
        """DataFrameの情報をログに出力する。

        Args:
            df (pd.DataFrame): ログ出力対象のDataFrame
        """
        info_type = tabulate_dataframe(df.dtypes.reset_index(), headers=['Columns', 'Type'])
        info_df = tabulate_dataframe(df)
        self.log_msg(f"DataFrame info_type:\n{info_type}", LogLevel.DEBUG)
        self.log_msg(f"DataFrame info_dataframe:\n{info_df}", LogLevel.INFO)
