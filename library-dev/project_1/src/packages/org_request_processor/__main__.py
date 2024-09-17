import pandas as pd
from src.lib.common_utils.ibr_enums import LogLevel

# config共有
from src.lib.common_utils.ibr_decorator_config import with_config
#import sys
#from src.lib.common_utils.ibr_decorator_config import initialize_config
#config = initialize_config(sys.modules[__name__])

from .excel_processor import ExcelProcessor
from .pre_processor import (
    DummyPreProcess1,
    DummyPreProcess2,
)
from .post_processor import (
    DummyPostProcess1,
    DummyPostProcess2,
)

from .processors_interface import ProcessorChain

# パッケージ例外定義
class ExcelProcessorError(Exception):
    """package独自例外"""

@with_config
class RequestProcessExecutor:
    """アプリケーションのメインクラス。

    Excelファイルの処理を制御し、エラーハンドリングを行う。

    Attributes:
        定義情報: dict
    """

    def __init__(self, config: dict | None = None):
        """Mainクラスのコンストラクタ。設定の読み込みと初期化を行う。"""
        # DI config
        self.config = config or self.config
        # custom logger
        self.log_msg = self.config.log_message

        self.processor_chain = ProcessorChain()


    def start(self) -> None:
        """アプリケーションのメイン処理を実行する"""
        # 処理開始
        self.log_msg("IBRDEV-I-0000001")

        # Excel処理インスタンス生成
        self.excel_processor = ExcelProcessor(self.config)

        # 前処理
        ## Excel日本語ColumnToPython変数マッピング
        dummpy_pre_process1 = DummyPreProcess1()
        dummpy_pre_process2 = DummyPreProcess2()
        self.processor_chain.add_pre_processor(dummpy_pre_process1)
        self.processor_chain.add_pre_processor(dummpy_pre_process2)
        self.processor_chain.execute_pre_processor(pd.DataFrame())

        # main処理 Validator/整合性チェク
        try:
            # validation実行
            _ = self.excel_processor.process_excel_validate()
        except Exception as e:
            err_msg = f"Unexpected error: {str(e)}"
            self.log_msg(err_msg, LogLevel.CRITICAL)
            raise ExcelProcessorError(err_msg) from e
        finally:
            # Validatorエラー検出
            if self.excel_processor.error_manager.has_errors():
                self.log_msg(f"Process completed with {len(self.excel_processor.error_manager.get_errors())} line validation errors", LogLevel.WARNING)
                self.log_msg(f"{self.excel_processor.result_validation_errors()}", LogLevel.WARNING)
            else:
                self.log_msg("Process completed successfully", LogLevel.INFO)

        # 後処理
        ## 統合レイアウトマッピング
        ## 動的ブラックリストチェック
        dummy_post_process1 = DummyPostProcess1()
        dummy_post_process2 = DummyPostProcess2()
        self.processor_chain.add_post_processor(dummy_post_process1)
        self.processor_chain.add_post_processor(dummy_post_process2)
        self.processor_chain.execute_post_processor(pd.DataFrame())

        # 処理終了ログ
        self.log_msg("IBRDEV-I-0000002")

if __name__ == '__main__':
    RequestProcessExecutor().start()
