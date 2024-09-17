from pydantic import BaseModel
from typing import Type

from src.model.dataclass.request_jinji_model import JinjiModel
from src.model.dataclass.request_kokuki_model import KokukiModel
from src.model.dataclass.request_kanren_model import KanrenModel

# config共有
from src.lib.common_utils.ibr_decorator_config import with_config
#import sys
#from src.lib.common_utils.ibr_decorator_config import initialize_config
#config = initialize_config(sys.modules[__name__])

@with_config
class ModelFactory:
    def create_model(self) -> Type[BaseModel]:
        pass

class JinjiModelFactory(ModelFactory):
    def create_model(self) -> Type[BaseModel]:
        return JinjiModel

class KokukiModelFactory(ModelFactory):
    def create_model(self) -> Type[BaseModel]:
        return KokukiModel

class KanrenModelFactory(ModelFactory):
    def create_model(self) -> Type[BaseModel]:
        return KanrenModel
