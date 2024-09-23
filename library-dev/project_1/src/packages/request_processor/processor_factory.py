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

from .kanren_processor import (
    KanrenPreProcessor,
    KanrenPostProcessor,
)

# config共有
from src.lib.common_utils.ibr_decorator_config import with_config
#import sys
#from src.lib.common_utils.ibr_decorator_config import initialize_config
#config = initialize_config(sys.modules[__name__])

@with_config
class ProcessorFactory():
    def create_pre_processor(self) -> PreProcessor:
        pass

    def create_post_processor(self) -> PostProcessor:
        pass


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


class KanrenProcessorFactory(ProcessorFactory):
    def create_pre_processor(self) -> PreProcessor:
        return KanrenPreProcessor()

    def create_post_processor(self) -> PostProcessor:
        return KanrenPostProcessor()


