# public library import
## sample import
import sys
from pathlib import Path

import pandas as pd

# project common library import
## sample import
from src.lib.common_utils.ibr_dataframe_helper import tabulate_dataframe
from src.lib.common_utils.ibr_decorator_config import initialize_config, with_config
from src.lib.common_utils.ibr_enums import LogLevel
from src.lib.common_utils.ibr_eventlog_handler import ProcessAlreadyRunningError, WindowsEventLogger
from src.lib.common_utils.ibr_mutex_check import MutexManager

# package library import
## sample import
from .model_factory import ModelFactory
from .validation_error_manager import ValidationErrorManager

# config取得
config = initialize_config(sys.modules[__name__])
log_msg = config.log_message
class Main:
    """アプリケーションのメインクラス

    DocString指摘形式で記載してください
    """
    def __init__(self, conf: dict|None=None):
        """Mainクラスのイニシャライザ。設定の読み込みと初期化を行う。"""
        # configのDI
        self.config = conf or config

        # configから構成要素取得
        self.env = self.config.env                       # env
        self.common_config = self.config.common_config   # common_config
        self.package_config = self.config.package_config # package_config
        self.log_msg = self.config.log_message           # カスタムロガー

        # その他初期処理

    # Class内関数
    def sample_function(self, param: str) -> str:
        pass

    # Class内,内部関数
    def _sample_inner_function(self, param: str) -> str:
        pass

    # 起動処理
    def start(self) -> None:
        """アプリケーションのメイン処理を実行する。"""
        self.log_msg("IBRDEV-I-0000001")  # 処理開始ログ

        # 何かしらの処理

        ## 共通ライブラリ部品での処理
        ## package個別ライブラリでの処理
        _df = pd.Dataframe()
        self.log_msg(f'\n\n{tabulate_dataframe(_df)}', LogLevel.INFO)

        self.log_msg("IBRDEV-I-0000002")  # 処理終了ログ

if __name__ == "__main__":
    try:
        # 多重起動抑制
        with MutexManager(__package__):
            Main.start()
    except ProcessAlreadyRunningError:
        err_msg = f"{__package__}は既に実行中です"
        log_msg(err_msg, LogLevel.WARNING)
    except Exception as e:
        err_msg = f"エラーが発生しました: {e}"
        log_msg(err_msg, LogLevel.ERROR)
        # 必要に応じて制御定義する
        ## WindowsEventlogにエラー出力しE-HUB検出する
        WindowsEventLogger.write_error_log(
            src="リファレンスアプリケーション",
            evt_id="3001",
            strings=["業務継続不可能エラー: ファイル障害", str(e)],
        )
