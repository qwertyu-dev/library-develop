"""環境設定情報生成,取得"""
import os
import socket
import sys
import traceback
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path
from typing import (
    Any,
)

from src.lib.common_utils.ibr_enums import (
    ExecEnvironment,
    LogLevel,
)
from src.lib.common_utils.ibr_logger_package import LoggerPackage
from src.lib.common_utils.ibr_toml_loader import TomlParser

################################
# logger
################################
logger = LoggerPackage(__package__)
log_msg = logger.log_message

################################
# class定義
################################
#@dataclass(frozen=True)
@dataclass()
class Config:
    """環境設定情報をConfigに設定

    - 各種設定値を取得しConfigObjectに詰め込み
    - 実装側は個別に初期設定を書かずにConfigObjectの支援を受けて実装する
        - 実行環境識別子
        - common_configへのパス
        - 各パッケージのpackage_configへのパス
        - カスタムロガーObject

    Copy right:
        (あとで書く)

    Args:
        ...

    Returns:
        (Config): 初期設定時を押し込めたConfigObject

    Raises:
        - Exception: ConfigObject構築中のエラー発生

    Example:
        >>> See. def load()

    Notes:
        テストコードを実行する際はOSの環境変数設定が必要になります
            - $Env:EXEC_PATTERN = 'tests'  or export EXEC_PATTERN=tests

        実行ホストからの環境識別やtomlファイルからの定義取得は個別に書かず
        ConfigObject生成の後、プロパティ生成で値取得すること

    Changelog:
        - v1.0.0 (2024/01/01): Initial release
        -
    """
    env: str
    common_config: dict
    package_config: dict
    log_message: Callable[[str, str|None, dict[str, Any]|None], None]

    @staticmethod
    def load(package_path: str|Path) -> dict:
        """環境設定情報をConfigObjectへロードする

        - 初期設定情報をConfigObjectへ格納します

        Copy right:
            (あとで書く)

        Args:
            package_path (str | Path): パッケージ毎にConfigを識別する,__package__を渡す想定

        Returns:
            (dict): 初期設定格納済dict

        Raises:
            - Exception: Config生成中のエラー発生

        Example:
            >> package_path = Path(__file__)
            >> config = Config.load(package_path)
            >> env = config.env
            >> COMMON_CONFIG = config.common_config
            >> PACKAGE_CONFIG = config.package_config
            >> log_msg = config.log_message
            >>> (sample code)

        Notes:
            _description_

        Changelog:
            - v1.0.0 (2024/01/01): Initial release
            -
        """
        package_path = Path(package_path)

        # src/tests を環境変数(EXEC_PATTERN)
        exec_pattern = os.environ.get('EXEC_PATTERN', 'src')

        # 1. 実行環境取得
        try:
            # hostnameから環境ラベル
            _hostname = socket.gethostname()
            env = ExecEnvironment.__members__.get(_hostname.upper(), ExecEnvironment.HOSTNAME_LOCAL).value
        except Exception as e:
            log_msg(f'実行環境判定処理に失敗しました: {e}',LogLevel.ERROR)
            tb = traceback.TracebackException.from_exception(e)
            log_msg(''.join(tb.format()), LogLevel.ERROR)
            raise

        # 2.common_config(固定)
        common_toml_path = Path(f'{exec_pattern}/def/common_config/common_config.toml')
        try:
            common_config = TomlParser.parse_toml_file(common_toml_path)
        except Exception as e:
            log_msg(f'common_config取得に失敗しました: {e}',LogLevel.ERROR)
            tb = traceback.TracebackException.from_exception(e)
            log_msg(''.join(tb.format()), LogLevel.ERROR)
            raise

        # 3.package_config(動的)
        package_current_dir = package_path.parent
        package_toml_path = package_current_dir / 'package_config.toml'
        try:
            package_config = TomlParser.parse_toml_file(package_toml_path)
        except Exception as e:
            log_msg(f'package_config取得に失敗しました: {e}',LogLevel.ERROR)
            tb = traceback.TracebackException.from_exception(e)
            log_msg(''.join(tb.format()), LogLevel.ERROR)
            raise

        # 4.カスタムロガーインスタンス
        try:
            logger = LoggerPackage()
            log_message = logger.log_message
        except Exception as e:
            log_msg(f'カスタムロガーインスタンス生成に失敗しました: {e}',LogLevel.ERROR)
            tb = traceback.TracebackException.from_exception(e)
            log_msg(''.join(tb.format()), LogLevel.ERROR)
            raise

        # 5.Mutexは入れない

        # 押し込めて返す
        # envにより指定環境定義ブロックを返す
        return Config(
            env,
            common_config[env],
            package_config[env],
            log_message,
        )

