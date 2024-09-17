import pandas as pd
from typing import Any

class Processor:
    def process(self, df: pd.DataFrame) -> pd.DataFrame:
        raise NotImplementedError

class PreProcessor(Processor):
    pass

class PostProcessor(Processor):
    pass

class Validator():
    def validate(self, data: Any) -> None:
        pass

class ProcessorChain:
    def __init__(self):
        self.pre_processors = []
        self.post_processors = []

    def add_pre_processor(self, processor: PreProcessor):
        self.pre_processors.append(processor)

    def add_post_processor(self, processor: PostProcessor):
        self.post_processors.append(processor)

    def execute_pre_processor(self, data: pd.DataFrame) -> pd.DataFrame:
        for processor in self.pre_processors:
            data = processor.process(data)
        return data

    def execute_post_processor(self, data: pd.DataFrame) -> pd.DataFrame:
        for processor in self.post_processors:
            data = processor.process(data)
        return data
