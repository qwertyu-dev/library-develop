from typing import Any

from .processor_interface import (
    PreProcessor,
    PostProcessor,
    Validator, 
)


class JinjiPreProcessor(PreProcessor):
    def process(self, data: Any) -> Any:
        print("Executing Jinji pre-processing")
        return data

class JinjiPostProcessor(PostProcessor):
    def process(self, data: Any) -> Any:
        print("Executing Jinji post-processing")
        return data

class JinjiValidator(Validator):
    def validate(self, data: Any) -> None:
        print("Executing Jinji Validation")
