from pathlib import Path
import pandas as pd

from src.lib.common_utils.ibr_dataframe_helper import tabulate_dataframe
from src.lib.common_utils.ibr_decorator_config import with_config
from src.lib.common_utils.ibr_enums import LogLevel
from src.lib.common_utils.ibr_excel_reader import ExcelDataLoader
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

        # decision table book path
        self.decision_table_path = Path(
            f"{self.common_config.get('decision_table_path', []).get('DECISION_TABLE_PATH', '')}/"
            f"{self.package_config.get('decision_table_file', []).get('DECISION_PRE_BOOK_NAME', '')}",
        )

        # decision table sheet name
        self.decision_table_sheet_name = (
            f"{self.package_config.get('decision_table_file', []).get('DECISION_PRE_SHEET_NAME','')}"
        )

        # Facade指定(受付orパターン編集をpackage_configで指定)
        self.preparation_import_facade = self.package_config.get('import_editor_facade', []).get('FACADE_IMPORT_PATH', '')

        self.log_msg(f'decision table book path: {self.decision_table_path}', LogLevel.INFO)
        self.log_msg(f'decision table sheet name : {self.decision_table_sheet_name}', LogLevel.INFO)
        self.log_msg(f'preparation import facade : {self.preparation_import_facade}', LogLevel.INFO)

    def get_decision_table(self)-> pd.DataFrame:
        excel_data_loader = ExcelDataLoader(
            self.decision_table_path,
        )
        _df = excel_data_loader.read_excel_one_sheet(
            self.decision_table_sheet_name,
            skiprows=1,
            usecols=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
        )

        # データ取り込みそのまま結果
        self.log_msg(f'decition_table: \n\n{tabulate_dataframe(_df)}')

        # column mapping
        decision_table_columns = [
            'facade_name_jp',
            'applicant_info',
            'target_org',
            'branch_code_digit',
            'business_and_area_code',
            'internal_sales_dept_code',
            'section_gr_code',
            'branch_code_first_digit',
            'branch_code_4_digits_application_status',
            'DecisionResult',
        ]
        _df.columns = decision_table_columns

        # 日本語Column→python Columnマッピング
        self.log_msg(f'decition_table: \n\n{tabulate_dataframe(_df)}')

        # definition mapping
        # チェック条件を関数名変換
        def replace_values(column):
            column = column.replace('4桁', 'is_4digits')
            column = column.replace('5桁', 'is_5digits')
            column = column.replace('なし', 'is_empy')
            column = column.replace('あり', 'is_not_empty')
            column = column.replace('^-$', 'any', regex=True)
            return column

        # 変換指定列に対してtransform
        columns_to_transform = [
            'branch_code_digit',
            'business_and_area_code',
            'internal_sales_dept_code',
            'section_gr_code',
            'branch_code_first_digit',
            'branch_code_4_digits_application_status',
        ]
        for col in columns_to_transform:
            _df[col] = replace_values(_df[col])

        # 判定関数pythonへマッピング
        self.log_msg(f'decition_table: \n\n{tabulate_dataframe(_df)}')
        return _df

    def start(self) -> None:
        """アプリケーションのメイン処理を実行する。"""
        try:
            self.log_msg("IBRDEV-I-0000001")  # 処理開始ログ

            # Facade定義読み込み
            decision_table = self.get_decision_table()

            # path生成
            # TODO(suzuki); 受付入力pickleファイルへのPathへ
            sample_data_path = Path(
                f"{self.common_config.get('optional_path', []).get('SHARE_RECEIVE_PATH', '')}/"
                f"{self.package_config.get('preparation_sample_data', []).get('PREPARATION_SAMPLE_DATA', '')}",
                )
            ## TODO(suzuki); ディシジョンテーブルpickleファイルへのPathへ
            self.decision_table_path = Path(
                f"{self.common_config.get('decision_table_path', []).get('DECISION_TABLE_PATH', '')}/"
                f"{self.package_config.get('decision_table_book_name', []).get('DECISION_TABLE_BOOK_NANE', '')}",
                )

            # Facade指定(受付orパターン編集をpackage_configで指定)
            preparation_import_facade = self.package_config.get('import_editor_facade', []).get('FACADE_IMPORT_PATH','')

            #self.log_msg(f'sample data path: {sample_data_path}', LogLevel.INFO)
            #self.log_msg(f'sample decision table path: {decision_table_path}', LogLevel.INFO)
            #self.log_msg(f'preparation import facade: {preparation_import_facade}', LogLevel.INFO)

            # データ取り込み
            # TODO(suzuki): read_pickleに置き換え
            data_sample = pd.read_excel(sample_data_path)

            # sample decision table
            decision_table = pd.read_excel(self.decision_table_path)

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
