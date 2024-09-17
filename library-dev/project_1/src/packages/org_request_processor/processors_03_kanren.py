from typing import Any

from .processor_interface import (
    PreProcessor,
    PostProcessor,
    Validator, 
)

class KanrenPreProcessor(PreProcessor):
    def process(self, data: Any) -> Any:
        print("Executing Kanren pre-processing")
        return data

class KanrenPostProcessor(PostProcessor):
    def process(self, data: Any) -> Any:
        print("Executing Kanren post-processing")
        return data

class KanrenValidator(Validator):
    def validate(self, data: Any) -> None:
        print("Executing Kanren Validation")
