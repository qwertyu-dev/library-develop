from pathlib import Path
import pandas as pd
from typing import List, Dict, Any, Tuple, Callable

from src.model.dataclass.sample_user_class import ExcelSampleModel
from src.lib.common_utils.ibr_enums import LogLevel
from src.lib.common_utils.ibr_dataframe_helper import tabulate_dataframe
from src.lib.common_utils.ibr_excel_reader import ExcelDataLoader
from src.lib.common_utils.ibr_get_config import Config
from src.lib.exceptions.business_exceptions import BusinessLogicError
from src.lib.validator_utils.validation_error_manager import ValidationErrorManager
from pydantic import ValidationError

class ExcelProcessor:
    """Excelファイルの処理とバリデーションを行うクラス。

    Attributes:
        file_path (Path): 処理対象のExcelファイルのパス
        sheet_name (str): 処理対象のシート名
        excel_loader (ExcelDataLoader): Excelファイルを読み込むためのローダー
        log_msg (Callable): ログメッセージを出力する関数
        error_manager (ValidationErrorManager): バリデーションエラーを管理するオブジェクト
    """

    def __init__(self, file_path: Path, sheet_name: str, log_msg: Callable):
        """ExcelProcessorのコンストラクタ。

        Args:
            file_path (Path): 処理対象のExcelファイルのパス
            sheet_name (str): 処理対象のシート名
            log_msg (Callable): ログメッセージを出力する関数
        """
        self.file_path = file_path
        self.sheet_name = sheet_name
        self.excel_loader = ExcelDataLoader(file_path=file_path)
        self.log_msg = log_msg
        self.error_manager = ValidationErrorManager(log_msg)

    def load_and_preprocess(self) -> pd.DataFrame:
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
        _df = self.excel_loader.read_excel_one_sheet(sheet_name=self.sheet_name)
        self._log_dataframe_info(_df)

        return _df


    def _log_dataframe_info(self, df: pd.DataFrame) -> None:
        """DataFrameの情報をログに出力する。

        Args:
            df (pd.DataFrame): ログ出力対象のDataFrame
        """
        info = tabulate_dataframe(df.dtypes.reset_index(), headers=['Columns', 'Type'])
        self.log_msg(f"DataFrame info:\n{info}", LogLevel.INFO)

    def validate(self, df: pd.DataFrame) -> None:
        """DataFrameの各行をバリデーションする。

        Args:
            df (pd.DataFrame): バリデーション対象のDataFrame
        """
        def _validate_row(row):
            try:
                ExcelSampleModel(**row.to_dict())
            except ValidationError as e:
                self.error_manager.add_validation_error(row.name, e)
            except Exception as e:
                self.log_msg(f"Unexpected error during validation at row {row.name}: {str(e)}", LogLevel.ERROR)
                self.error_manager.add_error(row.name, {"type": "unexpected_error", "msg": str(e)})

        df.apply(_validate_row, axis=1)

    def process_validation_errors(self) -> None:
        """バリデーションエラーを処理し、ログに出力する。"""
        self.error_manager.log_errors()

    def process_excel(self) -> pd.DataFrame:
        """Excelファイルの処理全体を実行する。

        Returns:
            pd.DataFrame: 処理済みのDataFrame
        """
        _df = self.load_and_preprocess()
        self.validate(_df)
        self.process_validation_errors()
        return _df


class ConfigLoader:
    @staticmethod
    def load_config():
        config = Config.load(__file__)
        return (
            config.env,
            config.common_config,
            config.package_config,
            config.log_messeage,
        )

class ExcelProcessorFactory:
    @staticmethid
    def create_processor(file_path, sheet_namem log_msg):

class Main:
    """アプリケーションのメインクラス。

    Excelファイルの処理を制御し、エラーハンドリングを行う。

    Attributes:
        env: 環境設定
        common_config: 共通設定
        package_config: パッケージ固有の設定
        log_msg: ログメッセージを出力する関数
        excel_file_path (Path): 処理対象のExcelファイルのパス
        excel_sheet_name (str): 処理対象のシート名
        excel_processor (ExcelProcessor): Excelファイルを処理するオブジェクト
    """

    def __init__(self):
        """Mainクラスのコンストラクタ。設定の読み込みと初期化を行う。"""
        config = Config.load(__file__)
        self.env = config.env
        self.common_config = config.common_config
        self.package_config = config.package_config
        self.log_msg = config.log_message

        self.excel_file_path = Path(
            f"{self.common_config['input_file_path']['UPDATE_EXCEL_PATH']}/"
            f"{self.package_config['excel_definition']['UPDATE_RECORD_JINJI']}",
        )
        self.excel_sheet_name = self.package_config['excel_definition']['UPDATE_RECORD_JINJI_SHEET_NAME']

        self.excel_processor = ExcelProcessor(self.excel_file_path, self.excel_sheet_name, self.log_msg)

    def start(self) -> None:
        """アプリケーションのメイン処理を実行する。

        Excelファイルの処理を行い、エラーハンドリングとログ出力を管理する。
        """
        self.log_msg("IBRDEV-I-0000001")  # 処理開始ログ
        try:
            # validation実行
            _ = self.excel_processor.process_excel()

            if self.excel_processor.error_manager.has_errors():
                self.log_msg(f"Process completed with {len(self.excel_processor.error_manager.get_errors())} validation errors", LogLevel.WARNING)
            else:
                self.log_msg("Process completed successfully", LogLevel.INFO)
        except BusinessLogicError as e:
            self.log_msg(f"Business logic error: {e.message}", LogLevel.ERROR)
            raise
        except Exception as e:
            self.log_msg(f"Unexpected error: {str(e)}", LogLevel.CRITICAL)
            raise
        finally:
            self.log_msg("IBRDEV-I-0000002")  # 処理終了ログ

if __name__ == '__main__':
    Main().start()
