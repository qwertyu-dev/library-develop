from pathlib import Path
from glob import glob

import pandas as pd

from src.lib.common_utils.ibr_dataframe_helper import tabulate_dataframe
from src.lib.common_utils.ibr_decorator_config import with_config
from src.lib.common_utils.ibr_enums import LogLevel
from src.lib.common_utils.ibr_excel_reader import ExcelDataLoader

from .file_configuration_factory import FileConfigurationFactory


class ExcelProcessorError(Exception):
    pass

class ExcelSheetColumnsUnmatchError(ValueError):
    pass

@with_config
class ExcelProcessor:
    """Excelファイルの処理とバリデーションを行うクラス"""

    def __init__(self, file_configuration_factory: FileConfigurationFactory, config: dict|None = None):
        self.config = config or self.config
        self.log_msg = self.config.log_message
        self.excel_file_pattern = file_configuration_factory.create_file_pattern()
        if not self.excel_file_pattern:
            err_msg = "Invalid file pattern: None"
            raise ExcelProcessorError(err_msg) from None
        self.excel_sheet_name = file_configuration_factory.create_sheet_name()
        self.excel_sheet_skiprows = file_configuration_factory.create_sheet_skiprows()
        self.excel_sheet_usecols = file_configuration_factory.create_sheet_usecols()

        self.log_msg(f"excel file pattern: {self.excel_file_pattern}", LogLevel.DEBUG)
        self.log_msg(f"excel sheet_name: {self.excel_sheet_name}", LogLevel.DEBUG)
        self.log_msg(f"excel sheet_skiprows: {self.excel_sheet_skiprows}", LogLevel.DEBUG)
        self.log_msg(f"excel sheet_usecols: {self.excel_sheet_usecols}", LogLevel.DEBUG)

    #def load(self) -> tuple[pd.DataFrame, list[str]]:
    def load(self) -> pd.DataFrame:
        dataframes = []
        common_columns = None

        for file_path in self.excel_file_pattern:
            self.log_msg(f'excel file path: {file_path}', LogLevel.INFO)
            try:
                _df = self._load_single_file(file_path)
                df, common_columns = self._validate_and_align_columns(_df, file_path, common_columns)
                #df_str = df.astype(str).replace('nan', '') # 全ての属性を文字列属性に変換i
                #dataframes.append(df_str)
                dataframes.append(df)
            except Exception as e:
                raise ExcelProcessorError from e

        return self._combine_dataframes(dataframes)

    def _load_single_file(self, file_path: Path) -> pd.DataFrame:
        excel_loader = ExcelDataLoader(file_path)
        return excel_loader.read_excel_one_sheet(
            sheet_name=self.excel_sheet_name,
            skiprows=self.excel_sheet_skiprows,
            usecols=self.excel_sheet_usecols,
            )

    def _validate_and_align_columns(self, df: pd.DataFrame, file_path: Path, common_columns: list[str] | None) -> tuple[pd.DataFrame, list[str]]:
        common_columns = common_columns or list(df.columns)
        self.log_msg(f'common_columns: {common_columns}', LogLevel.INFO)
        self.log_msg(f'df.columns; {df.columns}', LogLevel.INFO)
        if set(df.columns) != set(common_columns):
            err_msg = f'カラム構造が一致しないExcelBookがあります: {file_path}::{self.excel_sheet_name}'
            self.log_msg(err_msg, LogLevel.ERROR)
            raise ExcelSheetColumnsUnmatchError(err_msg)
        return df[common_columns], common_columns

    def _combine_dataframes(self, dataframes: list[pd.DataFrame]) -> pd.DataFrame:
        if not dataframes:
            return pd.DataFrame()
        combined_df = pd.concat(dataframes, ignore_index=True)
        self._log_dataframe_info(combined_df)
        return combined_df

    def _log_dataframe_info(self, df: pd.DataFrame) -> None:
        info_type = tabulate_dataframe(df.dtypes.reset_index(), headers=['Columns', 'Type'])
        info_df = tabulate_dataframe(df)
        self.log_msg(f"DataFrame info_type:\n{info_type}", LogLevel.DEBUG)
        self.log_msg(f"DataFrame info_dataframe:\n{info_df}", LogLevel.INFO)
