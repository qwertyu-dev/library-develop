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

class DataValidatorError(Exception):
    pass

@with_config
class DataValidator:
    def __init__(self, config: dict, validation_model: type[BaseModel]):
        if not isinstance(validation_model, type) or not issubclass(validation_model, BaseModel):
            err_msg = "validation_model must be a subclass of BaseModel"
            raise TypeError(err_msg) from None

        # DI config
        self.config = config or self.config

        self.validation_model = validation_model
        self.log_msg = self.config.log_message
        self.error_manager = ValidationErrorManager()

    def validate(self, df: pd.DataFrame) -> None:
        if df.empty:
            self.log_msg("Validation skipped: Empty DataFrame", LogLevel.INFO)
            return

        # validation実行制御
        df.apply(self._validate_row, axis=1)
        if self.error_manager.has_errors():
            self.result_validation_errors()
            self.log_msg(f'ValidateProcess completed with {len(self.error_manager.get_errors())} line validation errors', LogLevel.INFO)
        else:
            self.log_msg("Validation completed: No errors found", LogLevel.INFO)

    def _validate_row(self, row: pd.Series) -> None:
        # Validation実体
        # Error発生しても処理は継続(ValidationError,Exception)
        try:
            self.validation_model(**row.to_dict())
        except ValidationError as e:
            self.error_manager.add_validation_error(row.name if row.name is not None else 0, e)
        except Exception as e:
            self.log_msg(f"Unexpected error during validation at row {row.name if row.name is not None else 0}: {str(e)}", LogLevel.ERROR)
            self.error_manager.add_error(row.name if row.name is not None else 0, {"type": "unexpected_error", "msg": str(e)})

    def result_validation_errors(self) -> None:
        self.log_msg("result_validation_errors method called", LogLevel.DEBUG)
        self.error_manager.log_errors()
