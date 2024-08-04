import traceback

from pathlib import Path
import pandas as pd

from src.model.dataclass.sample_user_class import ExcelSampleModel
from src.lib.common_utils.ibr_enums import LogLevel
from src.lib.common_utils.ibr_dataframe_helper import tabulate_dataframe
#from src.lib.common_utils.ibr_mutex_check import MutexManager
from pydantic import ValidationError

from src.lib.common_utils.ibr_excel_reader import (
    ExcelDataLoader,
)

from src.lib.common_utils.ibr_get_config import Config


#####################################################
# main
#####################################################
class Main:
    def __init__(self):
        # 初期化情報取得
        config = Config.load(__file__)
        self._env = config.env
        self._COMMON_CONFIG = config.common_config
        self._PACKAGE_CONFIG = config.package_config
        self._log_msg = config.log_message

        # Validation対象Excel情報取得
        self._EXCEL_FILE_PATH = Path(
            f"{self._COMMON_CONFIG['input_file_path']['UPDATE_EXCEL_PATH']}/"
            f"{self._PACKAGE_CONFIG['excel_definition']['UPDATE_RECORD_JINJI']}",
        )
        self._EXCEL_SHEET_NAME = f"{self._PACKAGE_CONFIG['excel_definition']['UPDATE_RECORD_JINJI_SHEET_NAME']}"

        # インスタンス生成
        self._excel_loader = ExcelDataLoader(
            file_path=self._EXCEL_FILE_PATH,
        )

    def _excel_to_dataframe(self) -> pd.DataFrame:
        _df = self._excel_loader.read_excel_one_sheet(sheet_name='Sheet1')

        # EDA
        # 1.英語カラムへの変更をシミュレート
        _df = _df.rename(columns={
            'NO': 'No',
            'あ': 'a',
            'い': 'b',
            'う': 'c',
            'え': 'd',
            'お': 'e',
            'か': 'f',
            'き': 'g',
            'く': 'h',
            'け': 'i',
            'こ': 'j',
        },
        )

        # 2.余計な行を消す
        # キー列に値がないレコードは消す
        # キー列→ No列と今回は仮定している
        _df = _df.dropna(subset=['No'])

        # 3.型を定義
        #_df = _df.astype({
        #    'No': int,
        #    'a': str,
        #    'b': str,
        #    'c': int,
        #    'd': int,
        #    'e': int,
        #    'f': int,
        #    'g': str,
        #    'h': int,
        #    'i': int,
        #    'j': float,
        #},
        #)

        # TODO: 他EDAパターンの確認
        # 重複データの削除
        # 全角半角の統一
        # 大文字小文字の統一
        # 空白の削除
        # 特殊文字の扱い
        # indexのリセット

        # dataframe情報のログ出力
        # see. ibr_dataframe_helper.py
        self._log_msg(f"\n{tabulate_dataframe(_df.dtypes.reset_index(), headers=['Columns', 'Type'])}")

        return _df

    def _valdate(self, df: pd.DataFrame) -> bool:
        """_summary_

        Args:
            df (pd.DataFrame): _description_

        Returns:
            bool: _description_
        """
        _df = df.copy()

        # validatorチェック
        validate_errors = []
        for idx, row in enumerate(_df.itertuples(index=False)):
            try:
                _ = ExcelSampleModel(**row._asdict())
            except ValidationError as e:
                validate_errors.append((idx, e.errors()))
            except Exception as e:
                tb = traceback.TracebackException.from_exception(e)
                self._log_msg(''.join(tb.format()), LogLevel.ERROR)
                raise

        if len(validate_errors) > 0:
            # validate結果評価
            self._log_msg(f'検証対象ファイル: {self._EXCEL_FILE_PATH}', LogLevel.INFO)
            self._log_msg(f'検証対象Sheet: {self._EXCEL_SHEET_NAME}', LogLevel.INFO)
            self._log_msg(f'validate error 検出件数: {len(validate_errors)}', LogLevel.WARNING)
            self._log_msg(f'validate error list: {validate_errors}', LogLevel.DEBUG)
            _ = self._excel_loader.logger_validation_errors(validate_errors)

        return True


    def start(self) -> None:
        # start
        self._log_msg("IBRDEV-I-0000001")
        # バッチ2重起動チェック
        try:
            #with MutexManager(__package__):
            if True:
                # なにか
                _df = self._excel_to_dataframe()

                # validator
                self._valdate(_df)

        except Exception as e:
            tb = traceback.TracebackException.from_exception(e)
            self._log_msg(''.join(tb.format()), LogLevel.ERROR)
            raise

        self._log_msg("IBRDEV-I-0000002")

#####################################################
# 起動
#####################################################
if __name__ == '__main__':
    _main = Main()
    _main.start()
