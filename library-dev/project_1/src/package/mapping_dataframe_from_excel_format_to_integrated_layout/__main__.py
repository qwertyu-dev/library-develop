from pathlib import Path
import pandas as pd

from src.lib.common_utils.ibr_enums import LogLevel
from src.lib.common_utils.ibr_dataframe_helper import tabulate_dataframe
from src.lib.common_utils.ibr_get_config import Config

class Main:
    """アプリケーションのメインクラス。

    Excelファイルの処理を制御し、エラーハンドリングを行う。

    Attributes:
        env: 環境設定
        common_config: 共通設定
        package_config: パッケージ固有の設定
        log_msg: ログメッセージを出力する関数
    """

    def __init__(self):
        """Mainクラスのコンストラクタ。設定の読み込みと初期化を行う。"""
        config = Config.load(__file__)
        self.env = config.env
        self.common_config = config.common_config
        self.package_config = config.package_config
        self.log_msg = config.log_message

        from pprint import pprint
        pprint(self.env)
        pprint(self.package_config)

    def start(self) -> None:
        """アプリケーションのメイン処理を実行する。"""
        try:
            self.log_msg("IBRDEV-I-0000001")  # 処理開始ログ
        finally:
            self.log_msg("IBRDEV-I-0000002")  # 処理終了ログ

if __name__ == '__main__':
    Main().start()
