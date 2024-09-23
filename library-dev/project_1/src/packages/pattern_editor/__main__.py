from pathlib import Path
import pandas as pd

from src.lib.common_utils.ibr_dataframe_helper import tabulate_dataframe
from src.lib.common_utils.ibr_decorator_config import with_config
from src.lib.common_utils.ibr_enums import LogLevel
from src.model.factory.column_edit_facade_controller import (
    create_editor_factory,
    process_row,
)

@with_config
class PreparatonExecutor:
    """アプリケーションのメインクラス"""

    def __init__(self):
        """Mainクラスのイニシャライザ。設定の読み込みと初期化を行う。"""
        self.env = self.config.env
        self.common_config = self.config.common_config
        self.package_config = self.config.package_config
        self.log_msg = self.config.log_message

    def start(self) -> None:
        """アプリケーションのメイン処理を実行する。"""
        try:
            self.log_msg("IBRDEV-I-0000001")  # 処理開始ログ

            # path生成
            # TODO(suzuki); 受付入力pickleファイルへのPathへ
            sample_data_path = Path(
                f"{self.common_config.get('optional_path', []).get('SHARE_RECEIVE_PATH', '')}/"
                f"{self.package_config.get('preparation_sample_data', []).get('PREPARATION_SAMPLE_DATA', '')}",
                )
            # TODO(suzuki); ディシジョンテーブルpickleファイルへのPathへ
            decision_table_path = Path(
                f"{self.common_config.get('decision_table_path', []).get('DECISION_TABLE_PATH', '')}/"
                f"{self.package_config.get('decision_table_book_name', []).get('DECISION_TABLE_BOOK_NANE', '')}",
                )

            # Facade指定(受付orパターン編集をpackage_configで指定)
            preparation_import_facade = self.package_config.get('import_editor_facade', []).get('FACADE_IMPORT_PATH','')

            self.log_msg(f'sample data path: {sample_data_path}', LogLevel.INFO)
            self.log_msg(f'sample decision table path: {decision_table_path}', LogLevel.INFO)
            self.log_msg(f'preparation import facade: {preparation_import_facade}', LogLevel.INFO)

            # データ取り込み
            # TODO(suzuki): read_pickleに置き換え
            data_sample = pd.read_excel(sample_data_path)
            decision_table = pd.read_excel(decision_table_path)

            # 全ての列のデータ型を object に変更
            data_sample = data_sample.astype(object)
            decision_table = decision_table.astype(object)

            # factory生成
            factory = create_editor_factory(decision_table, preparation_import_facade)

            # 編集定義適用
            processed_data = data_sample.apply(lambda row: process_row(row, factory), axis=1)

            # 結果出力
            self.log_msg(f'\n{tabulate_dataframe(decision_table)}', LogLevel.INFO)
            self.log_msg(f'\n{tabulate_dataframe(data_sample)}', LogLevel.INFO)
            self.log_msg(f'\n{tabulate_dataframe(processed_data)}', LogLevel.INFO)

        finally:
            self.log_msg("IBRDEV-I-0000002")  # 処理終了ログ

if __name__ == '__main__':
    PreparatonExecutor().start()
