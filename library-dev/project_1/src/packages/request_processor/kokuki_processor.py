from typing import Any
import pandas as pd

from src.lib.common_utils.ibr_enums import LogLevel

from .processor_interface import (
    PreProcessor,
    PostProcessor,
)

from .mapping_excel_column_to_dataframe import (
    #JinjiExcelMapping,
    KokukiExcelMapping,
    #KanrenExcelMappingWithDummy,
    #KanrenExcelMappingWithoutDummy,
)

# chain詰め込み定義 Pre
## 名称ではなくObjectそのものを格納
class KokukiPreProcessor():
    def chain_pre_process(self) -> list[PreProcessor]:
        return [
            MapperProcessExcelColtoPythonColKokuki(),
            #DummyPreProcess1(),
            #DummyPreProcess2(),
        ]

# chain詰め込み定義 Post
## 名称ではなくObjectそのものを格納
class KokukiPostProcessor():
    def chain_post_process(self) -> list[PostProcessor]:
        return [
            #DummyPostProcess1(),
            #DummyPostProcess2(),
        ]

# pre process具体的な実体
class MapperProcessExcelColtoPythonColKokuki(PreProcessor):
    """日本語ExcelColをPython変数名にmapping"""
    def process(self, data: pd.DataFrame) -> pd.DataFrame:
        self.log_msg = self.config.log_message
        column_mapping_kokuki = KokukiExcelMapping()
        processed_data = data.copy()
        return column_mapping_kokuki.column_map(processed_data)

class DummyPreProcess1(PreProcessor):
    def process(self, data: pd.DataFrame) -> pd.DataFrame:
        self.log_msg = self.config.log_message
        processed_data = data.copy()
        # 何かしらの処理(processed_dataに対する軽微な編集処理を想定)
        # 次のClassに処理済データを渡す
        self.log_msg('execute pre process1', LogLevel.INFO)
        processed_data['new_column1'] = 'DummyPreProcess1'
        return processed_data

class DummyPreProcess2(PreProcessor):
    def process(self, data: pd.DataFrame) -> pd.DataFrame:
        self.log_msg = self.config.log_message
        processed_data = data.copy()
        # 何かしらの処理(processed_dataに対する軽微な編集処理を想定)
        self.log_msg('execute pre process2', LogLevel.INFO)
        processed_data['new_column2'] = 'DummyPreProcess2'
        return processed_data

class DummyPostProcess1(PostProcessor):
    def process(self, data: pd.DataFrame) -> pd.DataFrame:
        self.log_msg = self.config.log_message
        if data.empty:
            # 処理はバイパスして継続する
            err_msg = "Target DataFrame is empty..."
            self.log_msg(err_msg, LogLevel.INFO)
            return data

        processed_data = data.copy()
        # 何かしらの処理(軽微な編集処理を想定)
        # 何かしらの処理(processed_dataに対する軽微な編集処理を想定)
        self.log_msg('execute post process1', LogLevel.INFO)
        processed_data['new_column3'] = 'DummyPostProcess1'
        return processed_data

class DummyPostProcess2(PostProcessor):
    def process(self, data: pd.DataFrame) -> pd.DataFrame:
        self.log_msg = self.config.log_message
        processed_data = data.copy()
        # 何かしらの処理(processed_dataに対する軽微な編集処理を想定)
        self.log_msg('execute post process2', LogLevel.INFO)
        processed_data['new_column4'] = 'DummyPostProcess2'
        return processed_data

