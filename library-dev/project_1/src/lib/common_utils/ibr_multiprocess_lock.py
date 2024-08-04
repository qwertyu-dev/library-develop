import os
import fcntl
import traceback
import tempfile

from contextlib import contextmanager
from pathlib import Path

from src.lib.common_utils.ibr_enums import LogLevel
from src.lib.common_utils.ibr_file_operation_helper import delete_file
from src.lib.common_utils.ibr_logger_package import LoggerPackage

################################
# logger
################################
logger = LoggerPackage(__package__)
log_msg = logger.log_message

# 個別例外定義
class ProcessAlreadyRunningError(RuntimeError):
    """個別の例外定義、多重起動検出"""
    def __init__(self, process_name: str):
        super().__init__(f'Already running: {process_name}')

class LockFileDeleteError(RuntimeError):
    """個別の例外定義、多重起動検出"""
    def __init__(self, caller_package_name: str):
        super().__init__(f'lock file delete error: {caller_package_name}')


################################
# class定義
################################
class ProcessManager:
    """多重起動制御を行うクラス(プラットフォーム非依存)

    パッケージ起動単位で多重起動チェックを行う
    同一パッケージが起動中の場合は新たにパッケージ起動しないよう制御する
    この対応により想定外のデータ操作を回避する

    context managerで実装するため
        __enter__, __exit__を定義する

    Copy right:
        (あとで書く)

    Args:
        ...

    Returns:
        ...

    Raises:
        - Exception: Mutex制御中でのエラー発生

    Example:
        >>> with MutexManager:
        >>>    2重起動制御対象実装を書く

    Notes:
        ...

    Changelog:
        - v1.0.0 (2024/01/01): Initial release
        -
    """
    def __init__(self, caller_package_name: str) -> None:
        """起動lockファイル生成"""
        self.caller_package_name = caller_package_name

        # ファイル名を指定してロック制御ファイルを生成
        self.lock_file_path = Path(tempfile.gettempdir()) / f'{self.caller_package_name}.lock'
        self.lock_file = self.lock_file_path.open(mode='w')

    def __enter__(self):
        """起動ロックチェック"""
        try:
            fcntl.flock(self.lock_file.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        except OSError as e:
            log_msg(f'already runnning: {self.caller_package_name}', LogLevel.ERROR)
            raise ProcessAlreadyRunningError(self.caller_package_name) from e
        except Exception as e:
            log_msg(f'Failed to multiprocess check: {e}', LogLevel.ERROR)
            tb = traceback.TracebackException.from_exception(e)
            log_msg(''.join(tb.format()), LogLevel.ERROR)
            raise

    def __exit__(self, exc_type, exc_value, traceback):
        """起動lockファイル開放"""
        try:
            fcntl.flock(self.lock_file.fileno(), fcntl.LOCK_UN)
            self.lock_file.close()
        except Exception as e:
            log_msg(f'Failed to release lockfile: {e}', LogLevel.ERROR)
            tb = traceback.TracebackException.from_exception(e)
            log_msg(''.join(tb.format()), LogLevel.ERROR)
            raise
        try:
            self.lock_file_path.unlink()
        except Exception as e:
            log_msg(f'Failed to unlink lockfile: {e}', LogLevel.ERROR)
            tb = traceback.TracebackException.from_exception(e)
            log_msg(''.join(tb.format()), LogLevel.ERROR)
            raise

