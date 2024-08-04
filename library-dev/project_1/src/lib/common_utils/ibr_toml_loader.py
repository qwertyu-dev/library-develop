"""toml定義データをdictへ取得する処理をサポートするライブラリです"""
import traceback
from pathlib import Path

import toml
from src.lib.common_utils.ibr_enums import LogLevel
from src.lib.common_utils.ibr_logger_package import LoggerPackage

################################
# logger
################################
logger = LoggerPackage(__package__)
log_msg = logger.log_message

################################
# 関数定義
################################
class TomlParser:
    """tomlからのデータ取得を担当するClassです"""

    @staticmethod
    def parse_toml_file(toml_path: str|Path) -> dict|None:
        """指定したtoml定義をdictにロードします

        Copy right:
            (あとで書く)

        Args:
            toml_path (str | Path): toml定義ファイルパス

        Returns:
            (dict|None): tomlに定義した内容を保有するdict

        Raises:
            - FileNotFoundError
            - PermissionError
            - Exception

        Example:
            >>> TomlParser.parse_toml_file('./test.toml')

        Notes:
            _description_

        Changelog:
            - v1.0.0 (2024/01/01): Initial release
            -
        """
        toml_path = Path(toml_path)

        try:
            with toml_path.open(mode='r', encoding='utf8') as f:
                toml_obj = toml.load(f)
        except FileNotFoundError as e:
            log_msg(f'can not get target files {e}', LogLevel.ERROR)
            raise
        except PermissionError as e:
            log_msg(f'No permission to read the file: {e}', LogLevel.ERROR)
            raise
        except IsADirectoryError as e:
            log_msg(f'The specified path is a directory, not a file: {e}', LogLevel.ERROR)
            raise
        except TypeError as e:
            log_msg(f'Found invalid character in key: {e}', LogLevel.ERROR)
            raise
        except Exception as e:
            tb = traceback.TracebackException.from_exception(e)
            log_msg(''.join(tb.format()), LogLevel.ERROR)
            raise
        else:
            return toml_obj
