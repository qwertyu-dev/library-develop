"""Model定義"""

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    field_validator,
    model_validator,
)
from src.lib.validator_utils.field_validators import (
    name_must_contain_space,
    username_alphanumeric,
)
from src.lib.validator_utils.model_validators import (
    check_password_match,
)


class UserModel(BaseModel):
    # Item定義
    name: str = Field(...)
    username: str = Field(...)
    passoword1: str = Field(...)
    passoword2: str = Field(...)

    # 挙動定義
    model_config = ConfigDict(
        case_sensitive=True,
        validate_assignment=True,
        strict=True,
    )

    # field validator
    @field_validator('name')
    @classmethod
    def name_must_contain_space(cls, v: str) -> str:
        return name_must_contain_space(v)

    @field_validator('username')
    @classmethod
    def username_alphanumeric(cls, v: str) -> str:
        return username_alphanumeric

    @model_validator(mode='after')
    def check_password_match(self) -> 'UserModel':
        check_password_match(self.passoword1, self.passoword2)
        return self

class ExcelSampleModel(BaseModel):
    NO: int = Field(...)
    あ: str = Field(...)
    い: str = Field(...)
    う: int = Field(...)
    え: int = Field(...)
    お: int = Field(...)
    か: int = Field(...)
    き: str = Field(...)
    く: int = Field(...)
    け: int = Field(...)
    こ: float = Field(...)

    # 挙動定義
    model_config = ConfigDict(
        case_sensitive=True,
        validate_assignment=True,
        strict=True,
    )

    @field_validator('あ')
    @classmethod
    def is_alphabet_a(cls, v: str) -> str:
        if not v.isalpha():
            raise ValueError('field_a must be alphabet')
        return v

    @field_validator('い')
    @classmethod
    def is_alphabet_b(cls, v: str) -> str:
        if not v.isalpha():
            raise ValueError('field_a must be alphabet')
        return v

class ExcelSampleModel2(BaseModel):
    No: int = Field(...)
    a: str = Field(...)
    b: str = Field(...)
    c: int = Field(...)
    d: int = Field(...)
    e: int = Field(...)
    f: int = Field(...)
    g: str = Field(...)
    h: int = Field(...)
    i: int = Field(...)
    j: float = Field(...)

    # 挙動定義
    model_config = ConfigDict(
        case_sensitive=True,
        validate_assignment=True,
        strict=True,
    )

    @field_validator('a')
    @classmethod
    def is_alphabet_a(cls, v: str) -> str:
        if not v.isalpha():
            raise ValueError('field_a must be alphabet')
        return v

    @field_validator('b')
    @classmethod
    def is_alphabet_b(cls, v: str) -> str:
        if not v.isalpha():
            raise ValueError('field_a must be alphabet')
        return v