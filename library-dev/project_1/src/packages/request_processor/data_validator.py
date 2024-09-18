# data_validator.py
from pydantic import BaseModel, ValidationError
import pandas as pd

from src.lib.common_utils.ibr_enums import LogLevel
from .validation_error_manager import ValidationErrorManager

# config共有
from src.lib.common_utils.ibr_decorator_config import with_config
#import sys
#from src.lib.common_utils.ibr_decorator_config import initialize_config
#config = initialize_config(sys.modules[__name__])

@with_config
class DataValidator:
    def __init__(self, config: dict, validation_model: type[BaseModel]):
        # DI config
        self.config = config or self.config

        self.validation_model = validation_model
        self.log_msg = config.log_message
        self.error_manager = ValidationErrorManager(self.log_msg)

    def validate(self, df: pd.DataFrame) -> None:
        # validation実行制御
        df.apply(self._validate_row, axis=1)
        if self.error_manager.has_errors():
            self.result_validation_errors()
            self.log_msg(f'ValidateProcess complated with {len(self.error_manager.get_errors())} line validation errors', LogLevel.INFO)

    def _validate_row(self, row: pd.Series) -> None:
        # Validation実体
        try:
            self.validation_model(**row.to_dict())
        except ValidationError as e:
            self.error_manager.add_validation_error(row.name, e)
        except Exception as e:
            # 処理は継続
            self.log_msg(f"Unexpected error during validation at row {row.name}: {str(e)}", LogLevel.ERROR)
            self.error_manager.add_error(row.name, {"type": "unexpected_error", "msg": str(e)})

    def result_validation_errors(self) -> None:
        self.error_manager.log_errors()
