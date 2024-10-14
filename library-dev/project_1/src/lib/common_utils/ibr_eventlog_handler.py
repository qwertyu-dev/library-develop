"""WindowsEventlog出力ライブラリ"""
import sys
import traceback

# config共有
from src.lib.common_utils.ibr_decorator_config import (
    initialize_config,
)
from src.lib.common_utils.ibr_enums import LogLevel

# 実行環境によりimport切替
if sys.platform == 'win32':
    # Windowsライブラリインポート
    import pywintypes
    import win32con
    import win32evtlogutil
else:
    class DummyModule:
        # ダミーの定数を定義
        EVENTLOG_INFORMATION_TYPE = 0x0001
        EVENTLOG_WARNING_TYPE = 0x0002
        EVENTLOG_ERROR_TYPE = 0x0003

        ## ダミーの例外クラスを定義
        class error(Exception):
            pass

        ## ダミーの関数を定義
        @staticmethod
        def ReportEvent(*args, **kwargs):
            pass

    pywintypes = DummyModule()
    win32con = DummyModule()
    win32evtlogutil = DummyModule()

config = initialize_config(sys.modules[__name__])
log_msg = config.log_message

################################
# class
################################
class WindowsEventLoggerError(Exception):
    """WindowsEventLoggerパッケージ例外定義"""
class WindowsEventLogger:
    """WindowsEventlogへの出力を担当するクラス"""

    @classmethod
    def write_info_log(cls, src:str, evt_id: str, strings: list) -> None:
        """WindowsEventlogにinfoレベルの情報出力を行う

        Copy right:
            (あとで書く)

        Args:
            src (str): default= _description_
            evt_id (str): default= _description_
            strings (list): default= _description_

        Returns:
            ...

        Raises:
            - Exception: WindowsEventlog処理での例外発生

        Example:
            >>> WindowsEventLogger.write_info_log(
                    src='MySource test',
                    evt_id=1002,
                    strings=['This is a test'. 'info revel'],
                )
            >>> WindowsEventLogger.write_error_log(
                    src='MySource test',
                    evt_id=1003,
                    strings=['This is a error_test'. 'error revel'],
                )

        Notes:
            Windows環境に依存します
            testコードはmockによる呼び出し確認までに留めます

        Changelog:
            - v1.0.0 (2024/01/01): Initial release
            -
        """
        try:
            cls._write_eventlog(
                src=src,
                evt_id=evt_id,
                evt_type=win32con.EVENTLOG_INFORMATION_TYPE,
                strings=strings,
                data=None,
            )
        except Exception as e:
            tb = traceback.TracebackException.from_exception(e)
            log_msg(''.join(tb.format()), LogLevel.ERROR)
            raise WindowsEventLoggerError from e


    @classmethod
    def write_error_log(cls, src:str, evt_id: str, strings: list) -> None:
        """WindowsEventlogにerrorレベルの情報出力を行う

        Copy right:
            (あとで書く)

        Args:
            src (str): default= _description_
            evt_id (str): default= _description_
            strings (list): default= _description_

        Returns:
            ...

        Raises:
            - Exception: WindowsEventlog処理での例外発生

        Example:
            >>> WindowsEventLogger.write_error_log(
                    src=src,
                    evt_id=evt_id,
                    strings=strings,
                )

        Notes:
            Windows環境に依存します
            testコードはmockによる呼び出し確認までに留めます

        Changelog:
            - v1.0.0 (2024/01/01): Initial release
            -
        """
        try:
            cls._write_eventlog(
                src=src,
                evt_id=evt_id,
                evt_type=win32con.EVENTLOG_ERROR_TYPE,
                strings=strings,
                data=None,
            )
        except Exception as e:
            tb = traceback.TracebackException.from_exception(e)
            log_msg(''.join(tb.format()), LogLevel.ERROR)
            raise WindowsEventLoggerError from e

    @staticmethod
    def _write_eventlog(src: str, evt_id: int, evt_type: int, strings: list, data: str) -> None:
        """指定した情報を基にしてWindowsイベントログにメッセージ出力する

        Copy right:
            (あとで書く)

        Args:
            src (str): イベントソース
            evt_id (int): イベントID
            evt_type (int): イベントの種類
                # TODO Enum化の検討
                エラー: win32con.EVENTLOG_ERROR_TYPE
                情報  : win32con.EVENTLOG_INFORMATION_TYPE
                警告  : win32con.EVENTLOG_WARNING_TYPE
            strings (list): イベントの説明,複数指定可能でイベントービュアーでの表示はリストの順になる
            data (str): バイナリデータ,通常はNone

        Returns:
            None

        Raises:
            - pywintypes.error
            - Exception

        Example:
            >>> (sample code)

        Notes:
            _description_

        Changelog:
            - v1.0.0 (2024/01/01): Initial release
            -
        """
        # パラメータ受け取り
        _src = src
        _evt_id = evt_id
        _evt_type = evt_type
        _strings = strings
        _data = data

        # イベントログに書き出し
        try:
            win32evtlogutil.ReportEvent(
                appName=_src,
                eventID=_evt_id,
                eventType=_evt_type,
                string=_strings,
                data=_data,
            )
        except pywintypes.error as e:
            log_msg(f'eventlog write error: {e}')
            raise
        except Exception as e:
            tb = traceback.TracebackException.from_exception(e)
            log_msg (''.join(tb.format()), LogLevel.ERROR)
            raise WindowsEventLoggerError from e
