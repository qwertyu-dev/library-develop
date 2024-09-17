from pathlib import Path
import pandas as pd

# 受付処理
from src.model.factory.preparation_factory import create_editor_factory, process_row

from src.lib.common_utils.ibr_enums import LogLevel
from src.lib.common_utils.ibr_dataframe_helper import tabulate_dataframe
from src.lib.common_utils.ibr_get_config import Config

import sys
from src.lib.common_utils.ibr_decorator_config import initialize_config

# function
#config = initialize_config(sys.modules[__name__])

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
        #config = Config.load(__file__)
        self.config = config
        self.env = self.config.env
        self.common_config = self.config.common_config
        self.package_config = self.config.package_config
        self.log_msg = self.config.log_message

        # toml定義からの取り出し方法
        #pprint(self.package_config.get('layout', {}).get('unified_layout', []))

    def start(self) -> None:
        """アプリケーションのメイン処理を実行する。"""
        self.log_msg(self.env, LogLevel.INFO)
        self.log_msg(self.common_config['input_file_path']['UPDATE_EXCEL_PATH'], LogLevel.INFO)
        self.log_msg(self.common_config['decision_table_path']['DEF_DECISION_TABLE_PATH'], LogLevel.INFO)
        self.log_msg(self.package_config['decision_table_book_name']['DECISION_TABLE_BOOK_NANE'], LogLevel.INFO)
        self.log_msg(self.package_config['preparation_sample_data']['PREPARATION_SAMPLE_DATA'], LogLevel.INFO)

        try:
            self.log_msg("IBRDEV-I-0000001")  # 処理開始ログ

            # path生成
            sample_data_path = Path(
                f"{self.common_config['input_file_path']['UPDATE_EXCEL_PATH']}/"
                f"{self.package_config['preparation_sample_data']['PREPARATION_SAMPLE_DATA']}",
                )
            decision_table_path = Path(
                f"{self.common_config['decision_table_path']['DEF_DECISION_TABLE_PATH']}/"
                f"{self.package_config['decision_table_book_name']['DECISION_TABLE_BOOK_NANE']}",
                )

            self.log_msg(f'sample data path: {sample_data_path}')
            self.log_msg(f'sample decision table path: {decision_table_path}')

            # データ取り込み
            data_sample = pd.read_excel(sample_data_path)
            decision_table = pd.read_excel(decision_table_path)

            # 全ての列のデータ型を object に変更
            data_sample = data_sample.astype(object)
            decision_table = decision_table.astype(object)
            self.log_msg(f'\n{tabulate_dataframe(decision_table)}')

            # factory生成
            factory = create_editor_factory(decision_table)

            # 編集定義適用
            processed_data = data_sample.apply(lambda row: process_row(row, factory), axis=1)

            # 結果出力
            self.log_msg(f'\n{tabulate_dataframe(data_sample)}')
            self.log_msg(f'\n{tabulate_dataframe(processed_data)}')

        finally:
            self.log_msg("IBRDEV-I-0000002")  # 処理終了ログ

if __name__ == '__main__':
    Main().start()
