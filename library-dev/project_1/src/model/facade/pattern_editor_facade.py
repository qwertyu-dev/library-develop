# Facade定義
import pandas as pd

# base facade
from src.model.facade.base_facade import DataFrameEditor

from src.lib.common_utils.ibr_enums import LogLevel

# config共有
from src.lib.common_utils.ibr_decorator_config import with_config
#import sys
#from src.lib.common_utils.ibr_decorator_config import initialize_config
#config = initialize_config(sys.modules[__name__])

from src.lib.converter_utils.ibr_basic_column_editor import (
    ColumnEditor,
    Column1Editor,
    Column2Editor,
    Column3Editor,
    Column4Editor,
    Column5Editor,
    Column6Editor,
    Column7Editor,
    Column8Editor,
)

# 個別のColumnEditorを呼ぶ
# TODO(Suzuki): 個別編集部品をimportする



#TODO(suzuki): commonに入れるかどうかの判断
# ロギングHelper関数
def format_series_for_log(series: pd.Series) -> str:
    """Seriesオブジェクトを簡潔な文字列形式に変換します

    インデックス、dtype情報、Name情報を除去します。
    """
    return str(series.to_numpy().tolist())

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

        # 結果を返す
        return result
