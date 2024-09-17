import pandas as pd
from .processors_interface import PreProcessor
from .processors_interface import PostProcessor


class DummyPostProcess1(PostProcessor):
    def process(self, data: pd.DataFrame) -> pd.DataFrame:
        print('dummy post process1')
        return data

class DummyPostProcess2(PostProcessor):
    def process(self, data: pd.DataFrame) -> pd.DataFrame:
        print('dummy post process2')
        return data

