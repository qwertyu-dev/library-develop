from pathlib import Path
import pandas as pd
from typing import Callable

from src.model.dataclass.sample_user_class import ExcelSampleModel
from src.lib.common_utils.ibr_enums import LogLevel
from src.lib.common_utils.ibr_dataframe_helper import tabulate_dataframe
from .validation_error_manager import ValidationErrorManager
from pydantic import ValidationError

from src.lib.common_utils.ibr_excel_reader import ExcelDataLoader

# config共有
#import sys
from src.lib.common_utils.ibr_decorator_config import with_config
#from src.lib.common_utils.ibr_decorator_config import initialize_config
#config = initialize_config(sys.modules[__name__])

#@with_config
class ExcelProcessor:
    """Excelファイルの処理とバリデーションを行うクラス"""

    def __init__(self, config: dict | None = None):
        """ExcelProcessorのコンストラクタ。

        Args:
            file_path (Path): 処理対象のExcelファイルのパス
            sheet_name (str): 処理対象のシート名
            log_msg (Callable): ログメッセージを出力する関数
        """
        self.config = config

        # configから情報取得
        self.log_msg = config.log_message

        # Excelファイルパス生成/Sheet名生成
        self.excel_file_path = Path(
            f"{self.config.common_config['input_file_path']['UPDATE_EXCEL_PATH']}/"
            f"{self.config.package_config['excel_definition']['UPDATE_RECORD_JINJI']}",
        )
        self.excel_sheet_name = self.config.package_config['excel_definition']['UPDATE_RECORD_JINJI_SHEET_NAME']

        # インスタンス生成
        self.excel_loader = ExcelDataLoader(file_path=self.excel_file_path)
        self.error_manager = ValidationErrorManager(self.log_msg)


    def _load(self) -> pd.DataFrame:
        """Excelファイルを読み込み、前処理を行う。

        Returns:
            pd.DataFrame: 前処理済みのDataFrame
        Notes:
            取り込んだ後のDataFrameにEDA処理が必要ならば取り込んだ後に
            編集処理定義関数を呼び出すが、一括編集の役割では該当する処理は無い想定

            pydanticはExcel/DataFrameのcolumn名が日本語でも対応可能であると検証から確認
            案件ではcolumをPython名変換はするが一括申請フェーズではそのままで良いと判断
            受付処理では日本語column名で処理はしないのでmap変換してやる必要があります

        """
        _df = self.excel_loader.read_excel_one_sheet(sheet_name=self.excel_sheet_name)
        self._log_dataframe_info(_df)
        return _df


    def _log_dataframe_info(self, df: pd.DataFrame) -> None:
        """DataFrameの情報をログに出力する。

        Args:
            df (pd.DataFrame): ログ出力対象のDataFrame
        """
        info_type = tabulate_dataframe(df.dtypes.reset_index(), headers=['Columns', 'Type'])
        info_df = tabulate_dataframe(df)
        self.log_msg(f"DataFrame info_type:\n{info_type}", LogLevel.INFO)
        self.log_msg(f"DataFrame info_dataframe:\n{info_df}", LogLevel.INFO)

    def _validate(self, df: pd.DataFrame) -> None:
        """DataFrameの各行をバリデーションする。

        Args:
            df (pd.DataFrame): バリデーション対象のDataFrame
        """
        df.apply(self._validate_row, axis=1)

    def _validate_row(self, row: pd.Series) -> None:
        try:
            ExcelSampleModel(**row.to_dict())
        except ValidationError as e:
            # ValidationErrorを積み上げ
            self.error_manager.add_validation_error(row.name, e)
        except Exception as e:
            self.log_msg(f"Unexpected error during validation at row {row.name}: {str(e)}", LogLevel.ERROR)
            self.error_manager.add_error(row.name, {"type": "unexpected_error", "msg": str(e)})

    def process_excel_validate(self) -> pd.DataFrame:
        """Excelファイルの処理全体を実行する。

        Returns:
            pd.DataFrame: 処理済みのDataFrame
        """
        _df = self._load()
        self._validate(_df)
        return _df

    def result_validation_errors(self) -> None:
        """バリデーションエラーをログに出力する"""
        self.error_manager.log_errors()
