from pydantic import BaseModel
from typing import Type

from src.model.dataclass.request_processor_jinji_model import JinjiModel
from src.model.dataclass.request_processor_kokuki_model import KokukiModel
from src.model.dataclass.request_processor_kanren_with_model import KanrenWithModel
from src.model.dataclass.request_processor_kanren_without_model import KanrenWithoutModel

# config共有
from src.lib.common_utils.ibr_decorator_config import with_config
import sys
from src.lib.common_utils.ibr_decorator_config import initialize_config
config = initialize_config(sys.modules[__name__])

class ModelFactory:
    def create_model(self) -> Type[BaseModel]:
        raise NotImplementedError

class JinjiModelFactory(ModelFactory):
    def create_model(self) -> Type[BaseModel]:
        return JinjiModel

class KokukiModelFactory(ModelFactory):
    def create_model(self) -> Type[BaseModel]:
        return KokukiModel

class KanrenWithModelFactory(ModelFactory):
    def create_model(self) -> Type[BaseModel]:
        return KanrenWithModel

class KanrenWithoutModelFactory(ModelFactory):
    def create_model(self) -> Type[BaseModel]:
        return KanrenWithoutModel

