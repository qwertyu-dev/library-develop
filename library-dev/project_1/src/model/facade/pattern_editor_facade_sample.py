# Facade定義
import sys

import pandas as pd

# config共有
from src.lib.common_utils.ibr_decorator_config import initialize_config, with_config
from src.lib.common_utils.ibr_enums import LogLevel
from src.lib.converter_utils.ibr_basic_column_editor import (
    Column1Editor,
    Column2Editor,
    Column3Editor,
    ColumnEditor,
)

# 個別編集部品をimportする
# 各Facade要件及び編集部品品揃えからimport判断する
from src.lib.converter_utils.ibr_convert_western_cal_japanese_cal_to_datetime import parse_str_to_datetime

# base facade
from src.model.facade.base_facade import DataFrameEditor


#TODO(suzuki): commonに入れるかどうかの判断
# ロギングHelper関数
def format_series_for_log(series: pd.Series) -> str:
    """Seriesオブジェクトを簡潔な文字列形式に変換します

    インデックス、dtype情報、Name情報を除去します。
    """
    return str(series.to_numpy().tolist())

config = initialize_config(sys.modules[__name__])
log_msg = config.log_message

# どのcolumnに何の編集処理を適用するか定義している、Facadeそのもの
class DataFrameEditorDefault(DataFrameEditor):
    def __init__(self):
        super().__init__()

    def initialize_editors(self) -> dict[str, ColumnEditor]:
        return {
            'ulid':            Column1Editor(),
            'update_type':     Column2Editor(),
            'branch_code_bpr': Column3Editor(),
        }

    def edit_series(self, series: pd.Series) -> pd.Series:
        # 親クラス担当実施
        result = super().edit_series(series)
        self.log_msg(f'super edit series call result: {result}', LogLevel.INFO)
        self.log_msg(f'super edit series call result row.index: {result.index}', LogLevel.INFO)

        # ここに各Facade個別編集実装を列挙していく
        self.log_msg(f'\n\n個別Facade編集 result row.index: {result.index}', LogLevel.INFO)

        # sample edit
        result['xxxx'] = '荻野'
        result['xxxy'] = '斉藤'
        result['xxxz'] = '豊田'
        result['x2'] = parse_str_to_datetime('2024/10/25')   # importしたものを想定,サンプル編集
        result['x4'] = series['aaa'] + series['bbbb']

        # 結果を返す
        return self.reindex_series(result)
