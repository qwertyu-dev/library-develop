from typing import Any

from .processor_interface import (
    PreProcessor,
    PostProcessor,
    Validator, 
)


class KokukiPreProcessor(PreProcessor):
    def process(self, data: Any) -> Any:
        print("Executing Kokuki pre-processing")
        return data

class KokukiPostProcessor(PostProcessor):
    def process(self, data: Any) -> Any:
        print("Executing Kokuki post-processing")
        return data

class KokukiValidator(Validator):
    def validate(self, data: Any) -> None:
        print("Executing Kokuki Validation")
