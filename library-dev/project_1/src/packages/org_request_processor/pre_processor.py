import pandas as pd
from .processors_interface import PreProcessor
from .processors_interface import PostProcessor


class DummyPreProcess1(PreProcessor):
    def process(self, data: pd.DataFrame) -> pd.DataFrame:
        print('dummy pre process1')
        return data

class DummyPreProcess2(PreProcessor):
    def process(self, data: pd.DataFrame) -> pd.DataFrame:
        print('dummy pre process2')
        return data

