from typing import Any, Callable
from pydantic import ValidationError
from src.lib.common_utils.ibr_enums import LogLevel

class ValidationErrorManager:
    def __init__(self, logger: Callable):
        self.errors: list[tuple[int, list[dict[str, Any]]]] = []
        self.logger = logger

    def add_error(self, row_index: int, error: dict[str, Any]) -> None:
        """エラーを追加する"""
        self.errors.append((row_index, [error]))

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
        if self.has_errors():
            for row_index, errors in self.errors:
                for error in errors:
                    self.logger(f"Validation error at row {row_index}: {error}", LogLevel.WARNING)
        else:
            self.logger("No validation errors found", LogLevel.INFO)

    def clear_errors(self) -> None:
        """エラーリストをクリアする"""
        self.errors.clear()
