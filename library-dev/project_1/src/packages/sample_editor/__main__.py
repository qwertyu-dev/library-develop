from pathlib import Path
import pandas as pd

import logging
import json

from src.lib.common_utils.ibr_dataframe_helper import tabulate_dataframe
from src.lib.common_utils.ibr_decorator_config import with_config
from src.lib.common_utils.ibr_enums import LogLevel
from src.model.factory.column_edit_facade_controller import (
    create_editor_factory,
    process_row,
)

@with_config
class PreparatonExecutor:
    """アプリケーションのメインクラス"""

    def __init__(self):
        """Mainクラスのイニシャライザ。設定の読み込みと初期化を行う。"""
        self.env = self.config.env
        self.common_config = self.config.common_config
        self.package_config = self.config.package_config
        self.log_msg = self.config.log_message

    def start(self) -> None:
        """アプリケーションのメイン処理を実行する。"""
        try:
            self.log_msg("IBRDEV-I-0000001")  # 処理開始ログ
        finally:
            self.log_msg("IBRDEV-I-0000002")  # 処理終了ログ

def get_logger_config():
    root_logger = logging.getLogger()
    return {
        "level": logging.getLevelName(root_logger.level),
        "handlers": [
            {
                "class": type(handler).__name__,
                "level": logging.getLevelName(handler.level),
                "formatter": handler.formatter._fmt if handler.formatter else None,
                "filename": getattr(handler, 'baseFilename', None)
            }
            for handler in root_logger.handlers
        ],
        "disabled": root_logger.disabled
    }

def get_log_filename():
    root_logger = logging.getLogger()
    for handler in root_logger.handlers:
        if isinstance(handler, logging.handlers.TimedRotatingFileHandler):
            return handler.baseFilename
    return None

if __name__ == '__main__':
    print("Current Logger Configuration:")
    print(json.dumps(get_logger_config(), indent=2))
    print(f'{get_log_filename()}')

    PreparatonExecutor().start()
