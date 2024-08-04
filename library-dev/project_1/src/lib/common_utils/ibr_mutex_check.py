"""多重起動制御ライブラリ"""
from types import TracebackType

import win32api
import win32event
import winerror
from src.lib.common_utils.ibr_enums import LogLevel
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

################################
# 関数定義
################################
class MutexManager:
    """Windowsでの多重起動制御を行う

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
        >>> with MutexManager:]
        >>>    2重起動制御対象実装を書く

    Notes:
        ...

    Changelog:
        - v1.0.0 (2024/01/01): Initial release
        -
    """
    def __init__(self, caller_package_name: str) -> None:
        """Mutex生成"""
        # 多重起動制御開始
        log_msg('IBRDEV-I-0000004')

        # Mutex生成
        self.mutex = win32event.CreateMutex(None, False, caller_package_name) # noqa: FBT003 WindowsAPI仕様のためやむなし
        if win32api.GetLastError() == winerror.ERROR_ALREADY_EXISTS:
            log_msg(f'Already running: {caller_package_name}')
            raise ProcessAlreadyRunningError(caller_package_name)

    def __enter__(self): # noqa: D105 context managerのための実装、機能なしのため許容
        return self

    def __exit__(self, exc_type: type[BaseException]|None, exc_value: BaseException|None, traceback:TracebackType|None) -> None:
        """Mutex開放"""
        if self.mutex:
            try:
                win32api.CloseHandle(self.mutex)
            except Exception as e:
                log_msg(f'Failed to release mutex: {e}', LogLevel.ERROR)
                tb = traceback.TracebackException.from_exception(e)
                log_msg(''.join(tb.format()), LogLevel.ERROR)
                raise
            finally:
                # 多重起動制御終了
                log_msg('IBRDEV-I-0000005')
