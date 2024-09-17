from typing import Any
import pandas as pd

from src.lib.common_utils.ibr_enums import LogLevel

from .processor_interface import (
    PreProcessor,
    PostProcessor,
)

from .mapping_excel_column_to_dataframe import (
    JinjiExcelMapping,
    #KokukiExcelMapping,
    #KanrenExcelMappingWithDummy,
    #KanrenExcelMappingWithoutDummy,
)


# chain詰め込み定義 Pre
## 名称ではなくObjectそのものを格納
class JinjiPreProcessor():
    def chain_pre_process(self) -> list[PreProcessor]:
        return [
            MapperProcessExcelColtoPythonColJinji(),
            #DummyPreProcess1(),
            #DummyPreProcess2(),
        ]

# chain詰め込み定義 Post
"""たとえば

* 日本語Column名→Python変数名マッピング
** 部品はあるのでimportして実行するラッパー的なClassを作っていくイメージで良い

"""
## 名称ではなくObjectそのものを格納
class JinjiPostProcessor():
    def chain_post_process(self) -> list[PostProcessor]:
        return [
            #DummyPostProcess1(),
            #DummyPostProcess2(),
        ]

# pre process具体的な実体
class MapperProcessExcelColtoPythonColJinji(PreProcessor):
    """日本語ExcelColをPython変数名にmapping"""
    def process(self, df: pd.DataFrame) -> pd.DataFrame:
        self.log_msg = self.config.log_message
        column_mapping_jinji = JinjiExcelMapping()
        processed_data = df.copy()
        return column_mapping_jinji.column_map(processed_data)

class DummyPreProcess1(PreProcessor):
    def process(self, df: pd.DataFrame) -> pd.DataFrame:
        self.log_msg = self.config.log_message
        processed_data = df.copy()
        # 何かしらの処理(processed_dataに対する軽微な編集処理を想定)
        # 次のClassに処理済データを渡す
        self.log_msg('execute pre process1', LogLevel.INFO)
        processed_data['new_column1'] = 'DummyPreProcess1'
        self.log_msg(f"{self.config.package_config['excel_definition_mapping_jinji']}", LogLevel.DEBUG)
        self.log_msg(f"{self.config.package_config['layout']['unified_layout']}", LogLevel.DEBUG)
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
