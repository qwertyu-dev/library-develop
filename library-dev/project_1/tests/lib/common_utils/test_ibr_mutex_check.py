"""テスト実施方法

# project topディレクトリから実行する
$ pwd
/developer/library_dev/project_1

# pytest結果をファイル出力する場合
$ pytest -lv ./tests/lib/common_utils/test_ibr_csv_helper.py > tests/log/pytest_result.log

# pytest結果を標準出力する場合
$ pytest -lv ./tests/lib/common_utils/test_ibr_csv_helper.py
"""
import multiprocessing
from pathlib import Path
from unittest.mock import MagicMock

import pytest
import win32api
import win32event
import winerror

#####################################################################
# テスト実行環境セットアップ
#####################################################################
from src.lib.common_utils.ibr_enums import LogLevel
from src.lib.common_utils.ibr_get_config import Config

#####################################################################
# テスト対象モジュール import, project ディレクトリから起動する
#####################################################################
from src.lib.common_utils.ibr_mutex_check import (
    MutexManager,
)

package_path = Path(__file__)
config = Config.load(package_path)

log_msg = config.log_message
log_msg(str(config), LogLevel.DEBUG)

class Test_mutex_check:
    """ibr_mutex_checkのテスト全体をまとめたClass

    C0: 命令カバレッジ
    C1: 分岐カバレッジ
    C2: 条件カバレッジ
    """
    def test_mutex_manager_UT_C0_normal(self, mocker) -> None:
        # テスト定義ログ出力はこのまま書いてください、改修不要
        test_doc = """
        - テスト定義:
                - テストカテゴリ: C0
                - テスト区分: 正常系/UT
                - テストシナリオ:
        """
        test_functions = [func for func in dir(self) if callable(getattr(self, func)) and func.startswith('test')]
        func_info = f"        - テスト関数: {', '.join(test_functions)}"
        log_msg(f"\n{func_info}{test_doc}", LogLevel.DEBUG)

        # 結果定義,関数実行
        ## test1: Mutexが正常に作成される場合
        mocker.patch('win32event.CreateMutex', return_value=MagicMock())
        mocker.patch('win32api.GetLastError', return_value=0)
        mocker.patch('win32api.CloseHandle')

        with MutexManager('test_package'):
            win32event.event.CreateMutex.assert_call_once()
            win32api.GetLastError.assert_call_once()
            win32api.CloseHandle.assert_call_once()

        ## test2: Mutex作成時にエラーが発生する場合
        mocker.patch('win32event.CreateMutex', return_value=MagicMock())
        mocker.patch('win32api.GetLastError', return_value=winerror.ERROR_ALREADY_EXISTS)
        with pytest.raises(Exception):
            with MutexManager('test_package'):
                pass

        ## test: Mutex開放時にエラーが発生する場合
        mocker.patch('win32event.CreateMutex', return_value=MagicMock())
        mocker.patch('win32api.GetLastError', return_value=0)
        mocker.patch('win32api.CloseHandle', side_effect=Exception())
        with pytest.raises(Exception):
            with MutexManager('test_package'):
                pass


    def test_mutex_manager_UT_C0_normal_multiprocess(self, mocker) -> None:
        # テスト定義ログ出力はこのまま書いてください、改修不要
        test_doc = """
        - テスト定義:
                - テストカテゴリ: C0
                - テスト区分: 正常系/UT
                - テストシナリオ:
        """
        test_functions = [func for func in dir(self) if callable(getattr(self, func)) and func.startswith('test')]
        func_info = f"        - テスト関数: {', '.join(test_functions)}"
        log_msg(f"\n{func_info}{test_doc}", LogLevel.DEBUG)

        # 結果定義,関数実行
        def _worker(self):
            try:
                with MutexManager('test_package'):
                    pass
            except Exception:
                return 1
            else:
                return 0

        with multiprocessing.Pool(2) as p:
            results = p.map(self._worker, range(2))
        assert results.count(0) == 1
        assert results.count(1) == 1


    def test_mutex_manager_UT_C0_normal__init_(self, mocker) -> None:
        # テスト定義ログ出力はこのまま書いてください、改修不要
        test_doc = """
        - テスト定義:
                - テストカテゴリ: C0
                - テスト区分: 正常系/UT
                - テストシナリオ:
        """
        test_functions = [func for func in dir(self) if callable(getattr(self, func)) and func.startswith('test')]
        func_info = f"        - テスト関数: {', '.join(test_functions)}"
        log_msg(f"\n{func_info}{test_doc}", LogLevel.DEBUG)

        # 結果定義,関数実行
        ## test1 Mutexが正常に作成される場合
        mocker.patch('win32event.CreateMutex', return_value=MagicMock())
        mocker.patch('winapi.GetLastError', return_value=0)  # errorが発生しないことを示すもの
        mutex_manager = MutexManager('test_package')
        win32event.CreateMutex.assert_call_once()
        win32api.GetLastError.assert_call_once()

        # test2 Mutex作成時にエラーが発生する場合
        mocker.patch('win32event.CreateMutex', return_value=MagicMock())
        mocker.patch('win32api.GetLastError', return_value=winerror.ERROR_ALREADY_EXISTS)
        with pytest.raises(Exception):
            MutexManager('test_package')


    def test_mutex_manager_UT_C0_normal__exit__(self, mocker) -> None:
        # テスト定義ログ出力はこのまま書いてください、改修不要
        test_doc = """
        - テスト定義:
                - テストカテゴリ: C0
                - テスト区分: 正常系/UT
                - テストシナリオ:
        """
        test_functions = [func for func in dir(self) if callable(getattr(self, func)) and func.startswith('test')]
        func_info = f"        - テスト関数: {', '.join(test_functions)}"
        log_msg(f"\n{func_info}{test_doc}", LogLevel.DEBUG)

        # 結果定義,関数実行
        ## test1 Mutexが正常に開放される場合
        mocker.patch('win32event.CreateMutex', return_value=MagicMock())
        mocker.patch('win32api.GetLastError', return_value=0)
        mocker.patch('win32api.CloseHandle')
        mutex_manager = MutexManager('test_package')
        mutex_manager.__exit__(None, None, None)
        win32api.CloseHandle.assert_call_once()

        ## test2 Mutex開放時にエラーが発生する場合
        mocker.patch('win32event.CreateMutex', return_value=MagicMock())
        mocker.patch('win32api.GetLaseError', return_value=0)
        mocker.patch('win32api.CloseHandle', side_effect=Exception())
        mutex_manager = MutexManager('test_package')
        with pytest.raises(Exception):
            mutex_manager.__exit__(None, None, None)
