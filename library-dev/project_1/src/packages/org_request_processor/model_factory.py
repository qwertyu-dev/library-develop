from pydantic import BaseModel
from src.model.dataclass.request_jinji_model import (
    JinjiModel,
    KokukiModel,
    KanrenModel,
)
from typing import Type

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
