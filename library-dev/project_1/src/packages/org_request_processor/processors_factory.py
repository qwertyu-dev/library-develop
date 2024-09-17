from .processor_interface import (
    PreProcessor,
    PostProcessor,
    Validator,
)
from .jinji_Processors import (
    JinjiPreProcessor,
    JinjiPostProcessor,
    JinjiValidator,
)

from .kokuki_processors import (
    KokukiPreProcessor,
    KokukiPostProcessor,
    KokukiValidateator,
)

from .kanren_processors import (
    KanrenPreProcessor,
    KanrenPostProcessor,
    KanrenValidator,
)

class ProcessorFactory():
    def create_pre_processor(self) -> PreProcessor:
        pass

    def create_post_processor(self) -> PostProcessor:
        pass

    def create_validator(self) -> Validator:
        pass

class JinjiProcessorFactory(ProcessorFactory):
    def craate_pre_processor(self) -> PreProcessor:
        return JinjiPreProcessor()

    def craate_post_processor(self) -> PostProcessor:
        return JinjiPostProcessor()

    def craate_validator(self) -> Validator:
        return JinjiValidator()

class KokukiProcessorFactory(ProcessorFactory):
    def create_pre_processor(self) -> PreProcessor:
        return KokukiPreProcessor()

    def create_post_processor(self) -> PostProcessor:
        return KokukiPostProcessor()

    def validator(self) -> Validator:
        return KokukiValidateator()

class KanrenProcessorFactory(ProcessorFactory):
    def create_pre_processor(self) -> PreProcessor:
        return KanrenPreProcessor()

    def create_post_processor(self) -> PostProcessor:
        return KanrenPostProcessor()

    def create_validator(self):
        return KanrenValidator()

