from typing import Any, Callable
from pydantic import ValidationError

from src.lib.common_utils.ibr_enums import LogLevel
from src.lib.common_utils.ibr_logger_helper import format_dict

# config共有
from src.lib.common_utils.ibr_decorator_config import with_config

#import sys
#from src.lib.common_utils.ibr_decorator_config import initialize_config
#config = initialize_config(sys.modules[__name__])

@with_config
class ValidationErrorManager:
    def __init__(self, config: dict|None = None):
        # DI
        self.log_msg = config or self.config.log_message

        # エラー入れ物初期化
        self.errors: list[tuple[int, list[dict[str, Any]]]] = []

    def add_error(self, row_index: int|str, error_info: dict[str, Any]) -> None:
        """Exception発生時のエラーを追加する,Validation処理中の想定外エラー"""
        self.errors.append((row_index, [error_info]))
        #if row_index not in self.errors:
        #    self.errors[row_index] = []
        #self.errors[row_index].append(error_info)

    def add_validation_error(self, row_index: int, validation_error: ValidationError) -> None:
        """ValidationErrorをエラーリストに追加する"""
        self.errors.append((row_index, validation_error.errors()))

    def has_errors(self) -> bool:
        """エラーがあるかどうかを返す"""
        return len(self.errors) > 0

    def get_errors(self) -> list[tuple[int, list[dict[str, Any]]]]:
        """全エラーを取得する"""
        return self.errors

    def log_errors(self) -> None:
        """エラーをログに出力する"""
        self.log_msg(f'{self.has_errors()}', LogLevel.INFO)

        if self.has_errors():
            for row_index, errors in self.get_errors():
                for error in errors:
                    error_msg = format_dict(error)
                    #self.log_msg(f"Validation error at row {row_index}: \n{error_msg}", LogLevel.WARNING)
                    self.log_msg(f"Validation error at row {row_index}: \n{error_msg}", LogLevel.DEBUG)
        else:
            self.log_msg("No validation errors found", LogLevel.INFO)

    def clear_errors(self) -> None:
        """エラーリストをクリアする"""
        self.errors.clear()
