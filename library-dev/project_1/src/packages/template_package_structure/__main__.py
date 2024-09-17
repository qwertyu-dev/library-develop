from pathlib import Path
import pandas as pd


from src.lib.common_utils.ibr_enums import LogLevel
from src.lib.common_utils.ibr_dataframe_helper import tabulate_dataframe
from src.lib.common_utils.ibr_get_config import Config

# test
from src.lib.common_utils.ibr_file_operation_helper import copy_file
from src.lib.common_utils.ibr_file_operation_helper import move_file

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
        """Mainクラスのイニシャライザ。設定の読み込みと初期化を行う。"""
        config = Config.load(__file__)
        self.env = config.env
        self.common_config = config.common_config
        self.package_config = config.package_config
        self.log_msg = config.log_message

        # toml定義からの取り出し方法
        # self.package_config.get('layout', {}).get('unified_layout', [])


    def start(self) -> None:
        """アプリケーションのメイン処理を実行する。"""
        self.log_msg("IBRDEV-I-0000001")  # 処理開始ログ

        try:
            copy_file(Path('/tmp/file_move_test.txt'), Path('/tmp'), with_timestamp=1)
            move_file(Path('/tmp/file_move_test.txt'), Path('/tmp'))
        finally:
            self.log_msg("IBRDEV-I-0000002")  # 処理終了ログ

if __name__ == '__main__':
    Main().start()
