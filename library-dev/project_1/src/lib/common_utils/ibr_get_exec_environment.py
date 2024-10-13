from dataclasses import dataclass
import os
import sys

from src.lib.common_utils.ibr_enums import LogLevel
from src.lib.common_utils.ibr_decorator_config import initialize_config
config = initialize_config(sys.modules[__name__])
log_msg = config.log_message

@dataclass(flozen=True)
class OSEnvConfig:
    DEFAULT_EXEC_PATTERN = 'src'

def get_os_env_exec_pattern() -> str:
    """os環境変数: EXEC_PATTERN 設定値を取得する"""
    os_env_exec_pattern = os.environ.get('EXEC_PATTERN', OSEnvConfig.DEFAULT_EXEC_PATTERN)
    log_msg(f'OS環境変数: EXEC_PATTERN: {os_env_exec_pattern}', LogLevel=LogLevel.INFO)
    return os_env_exec_pattern
