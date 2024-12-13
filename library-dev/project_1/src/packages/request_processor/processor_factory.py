from src.model.processor_chain.processor_interface import (
    PreProcessor,
    PostProcessor,
)

from .jinji_processor import (
    JinjiPreProcessor,
    JinjiPostProcessor,
)

from .kokuki_processor import (
    KokukiPreProcessor,
    KokukiPostProcessor,
)

from .kanren_with_processor import (
    KanrenWithPreProcessor,
    KanrenWithPostProcessor,
)
from .kanren_without_processor import (
    KanrenWithoutPreProcessor,
    KanrenWithoutPostProcessor,
)


# config共有
from src.lib.common_utils.ibr_decorator_config import with_config
#import sys
#from src.lib.common_utils.ibr_decorator_config import initialize_config
#config = initialize_config(sys.modules[__name__])

class ProcessorFactory():
    def create_pre_processor(self) -> PreProcessor:
        raise NotImplementedError

    def create_post_processor(self) -> PostProcessor:
        raise NotImplementedError


class JinjiProcessorFactory(ProcessorFactory):
    def create_pre_processor(self) -> PreProcessor:
        return JinjiPreProcessor()

    def create_post_processor(self) -> PostProcessor:
        return JinjiPostProcessor()


class KokukiProcessorFactory(ProcessorFactory):
    def create_pre_processor(self) -> PreProcessor:
        return KokukiPreProcessor()

    def create_post_processor(self) -> PostProcessor:
        return KokukiPostProcessor()


class KanrenWithProcessorFactory(ProcessorFactory):
    def create_pre_processor(self) -> PreProcessor:
        return KanrenWithPreProcessor()

    def create_post_processor(self) -> PostProcessor:
        return KanrenWithPostProcessor()

class KanrenWithoutProcessorFactory(ProcessorFactory):
    def create_pre_processor(self) -> PreProcessor:
        return KanrenWithoutPreProcessor()

    def create_post_processor(self) -> PostProcessor:
        return KanrenWithoutPostProcessor()



