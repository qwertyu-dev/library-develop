"""テスト実施方法

# project topディレクトリから実行する
$ pwd
/developer/library_dev/project_1

# pytest結果をファイル出力する場合
$ pytest -lv ./tests/lib/common_utils/test_ibr_csv_helper.py > tests/log/pytest_result.log

# pytest結果を標準出力する場合
$ pytest -lv ./tests/lib/common_utils/test_ibr_csv_helper.py
"""
from pathlib import Path
from unittest.mock import MagicMock

import fcntl
import pytest
import threading
import time

#####################################################################
# テスト対象モジュール import, project ディレクトリから起動する
#####################################################################
from src.lib.common_utils.ibr_multiprocess_lock import (
    ProcessManager,
    ProcessAlreadyRunningError,
    LockFileDeleteError,
)
from src.lib.common_utils.ibr_file_operation_helper import delete_file

#####################################################################
# テスト実行環境セットアップ
#####################################################################
from src.lib.common_utils.ibr_enums import LogLevel
from src.lib.common_utils.ibr_get_config import Config

package_path = Path(__file__)
config = Config.load(package_path)

log_msg = config.log_message
log_msg(str(config), LogLevel.DEBUG)

####################################################
# helper関数
####################################################
def _worker():
    try:
        with ProcessManager('test_package'):
            time.sleep(10)
    except Exception:
        return 1
    else:
        return 0

class Test_multiprocess_lock_processmanager:
    """ibr_multiprocess_lockのテスト全体をまとめたClass

    C0: 命令カバレッジ
    C1: 分岐カバレッジ
    C2: 条件カバレッジ
    """
    def test_processmanager_UT_C0_normal(
        self,
        mocker:MagicMock,
        caplog: pytest.LogCaptureFixture,
        capfd: pytest.LogCaptureFixture,
        ) -> None:
        # テスト定義ログ出力はこのまま書いてください、改修不要
        test_doc = """
        - テスト定義:
                - テストカテゴリ: C0
                - テスト区分: 正常系/UT
                - テストシナリオ:
                    with ProcessManager('test_package'): ステートメントを使用すると
                    ProcessManager クラスのインスタンスがコンテキストマネージャとして機能します。
                    Pythonのコンテキストマネージャは、with ステートメントのブロックに入る際に
                    __enter__ メソッドを呼び出し、ブロックを抜ける際に __exit__ メソッドを呼び出します。

                    このテストケースでは、ProcessManager の __enter__ メソッドが呼び出されると
                    fcntl.flock を使用してファイルロックを試みます。
                    これは、プロセスが排他的にリソースを使用することを保証するためです。
                    with ブロックを抜けると、ProcessManager の __exit__ メソッドが呼び出され
                    fcntl.flock を使用してファイルロックを解放します。

                    呼び出しの引数は、最初が (5, 6) で、2回目が (5, 8) です。
                    5 はファイル記述子
                    6 は fcntl.LOCK_EX | fcntl.LOCK_NB(排他的ロックを試みる)
                    8 は fcntl.LOCK_UN(ロックの解放)
                    を表しています。
        """
        test_functions = [func for func in dir(self) if callable(getattr(self, func)) and func.startswith('test')]
        func_info = f"        - テスト関数: {', '.join(test_functions)}"
        log_msg(f"\n{func_info}{test_doc}", LogLevel.DEBUG)

        #####################################
        # ケース 通常処理
        #####################################
        # ファイルロック制御 呼び出し回数予想(ロック及び開放)
        expected_called_count = 2

        # 結果定義,関数実行
        mock_flock =  mocker.patch('fcntl.flock')
        with ProcessManager('test_package'):
                pass # __enter__が呼ばれる

        # fcntl.flockがロック取得のために呼び出されたことを確認
        mock_flock.assert_any_call(mocker.ANY, fcntl.LOCK_EX | fcntl.LOCK_NB)

        # fcntl.flockがロック解放のために呼び出されたことを確認
        mock_flock.assert_any_call(mocker.ANY, fcntl.LOCK_UN)

        # fcntl.flockの呼び出し回数を確認
        assert mock_flock.call_count == expected_called_count


    def test_processmanager_enter_UT_C0_oserror(
        self,
        mocker:MagicMock,
        caplog: pytest.LogCaptureFixture,
        capfd: pytest.LogCaptureFixture,
        ) -> None:
        # テスト定義ログ出力はこのまま書いてください、改修不要
        test_doc = """
        - テスト定義:
                - テストカテゴリ: C0
                - テスト区分: 正常系/UT
                - テストシナリオ: ロック作成時にエラー OSErrorが発生する場合
        """
        test_functions = [func for func in dir(self) if callable(getattr(self, func)) and func.startswith('test')]
        func_info = f"        - テスト関数: {', '.join(test_functions)}"
        log_msg(f"\n{func_info}{test_doc}", LogLevel.DEBUG)

        # caplogを使ってログメッセージをキャプチャ
        caplog.set_level(LogLevel.ERROR.value)

        # 期待されるログメッセージ
        expected_log_msg = "already runnning"

        mock_flock =  mocker.patch('fcntl.flock', side_effect=[OSError, None])
        with pytest.raises(ProcessAlreadyRunningError):
            with ProcessManager('test_package'):
                pass

        # 結果評価
        # キャプチャされたログメッセージを取得
        captured_logs = caplog.text
        assert expected_log_msg in captured_logs, f"Expected log message '{expected_log_msg}' to be in captured logs, but it was not. Captured logs: '{captured_logs}'"


    def test_processmanager_enter_UT_C0_exception(
        self,
        mocker:MagicMock,
        caplog: pytest.LogCaptureFixture,
        capfd: pytest.LogCaptureFixture,
        ) -> None:
        # テスト定義ログ出力はこのまま書いてください、改修不要
        test_doc = """
        - テスト定義:
                - テストカテゴリ: C0
                - テスト区分: 正常系/UT
                - テストシナリオ: ロック作成時にエラー Exceptionが発生する場合
        """
        test_functions = [func for func in dir(self) if callable(getattr(self, func)) and func.startswith('test')]
        func_info = f"        - テスト関数: {', '.join(test_functions)}"
        log_msg(f"\n{func_info}{test_doc}", LogLevel.DEBUG)
        # caplogを使ってログメッセージをキャプチャ
        caplog.set_level(LogLevel.ERROR.value)

        # 期待されるログメッセージ
        expected_log_msg = "Failed to multiprocess check"

        mock_flock =  mocker.patch('fcntl.flock', side_effect=[Exception, None])
        with pytest.raises(Exception):
            with ProcessManager('test_package'):
                pass

        # 結果評価
        # キャプチャされたログメッセージを取得
        captured_logs = caplog.text
        assert expected_log_msg in captured_logs, f"Expected log message '{expected_log_msg}' to be in captured logs, but it was not. Captured logs: '{captured_logs}'"


    def test_processmanager_exit_UT_C0_exception(
        self,
        mocker:MagicMock,
        caplog: pytest.LogCaptureFixture,
        capfd: pytest.LogCaptureFixture,
        ) -> None:
        # テスト定義ログ出力はこのまま書いてください、改修不要
        test_doc = """
        - テスト定義:
                - テストカテゴリ: C0
                - テスト区分: 正常系/UT
                - テストシナリオ: ロック開放時にエラー Exceptionが発生する場合
        """
        test_functions = [func for func in dir(self) if callable(getattr(self, func)) and func.startswith('test')]
        func_info = f"        - テスト関数: {', '.join(test_functions)}"
        log_msg(f"\n{func_info}{test_doc}", LogLevel.DEBUG)

        # caplogを使ってログメッセージをキャプチャ
        caplog.set_level(LogLevel.ERROR.value)

        # 期待されるログメッセージ
        expected_log_msg = "Failed to release lockfile"

        mock_flock =  mocker.patch('fcntl.flock', side_effect=[None, Exception])
        with pytest.raises(Exception):
            with ProcessManager('test_package'):
                pass

        # 結果評価
        # キャプチャされたログメッセージを取得
        captured_logs = caplog.text
        assert expected_log_msg in captured_logs, f"Expected log message '{expected_log_msg}' to be in captured logs, but it was not. Captured logs: '{captured_logs}'"


    def test_processmanager_exit_UT_C0_delete_file_error_exception(
        self,
        mocker:MagicMock,
        caplog: pytest.LogCaptureFixture,
        capfd: pytest.LogCaptureFixture,
        ) -> None:
        # テスト定義ログ出力はこのまま書いてください、改修不要
        test_doc = """
        - テスト定義:
                - テストカテゴリ: C0
                - テスト区分: 正常系/UT
                - テストシナリオ: ロック開放時にエラー Exceptionが発生する場合
        """
        test_functions = [func for func in dir(self) if callable(getattr(self, func)) and func.startswith('test')]
        func_info = f"        - テスト関数: {', '.join(test_functions)}"
        log_msg(f"\n{func_info}{test_doc}", LogLevel.DEBUG)

        # caplogを使ってログメッセージをキャプチャ
        caplog.set_level(LogLevel.ERROR.value)

        # 期待されるログメッセージ
        expected_log_msg = "Failed to unlink lockfile"

        #mocker.patch('src.lib.common_utils.ibr_file_operation_helper.delete_file', side_effect=Exception)
        mocker.patch('pathlib.Path.unlink', side_effect=Exception)
        with pytest.raises(Exception):
            with ProcessManager('test_package'):
                pass

        # 結果評価
        # キャプチャされたログメッセージを取得
        captured_logs = caplog.text
        assert expected_log_msg in captured_logs, f"Expected log message '{expected_log_msg}' to be in captured logs, but it was not. Captured logs: '{captured_logs}'"


    def test_mutex_manager_UT_C0_normal_multiprocess(
        self,
        mocker:MagicMock,
        caplog: pytest.LogCaptureFixture,
        capfd: pytest.LogCaptureFixture,
        ) -> None:
        # テスト定義ログ出力はこのまま書いてください、改修不要
        test_doc = """
        - テスト定義:
                - テストカテゴリ: C0
                - テスト区分: 正常系/UT
                - テストシナリオ: 複数起動してalready runningの検出を確認する
                    multiprocessing と caplog を直接組み合わせて使用することはできません。
                    なぜなら、multiprocessing は新しいプロセスを作成しそれぞれのプロセスは
                    独自のメモリ空間を持つためメインプロセスの caplog フィクスチャに
                    アクセスできないからです。
                    この問題を解決するためには、multiprocessing の代わりに
                    threading モジュールを使用しています。
        """
        test_functions = [func for func in dir(self) if callable(getattr(self, func)) and func.startswith('test')]
        func_info = f"        - テスト関数: {', '.join(test_functions)}"
        log_msg(f"\n{func_info}{test_doc}", LogLevel.DEBUG)

        # caplogを使ってログメッセージをキャプチャ
        caplog.set_level(LogLevel.ERROR.value)

        # 期待されるログメッセージ
        expected_log_msg_1 = "__enter__"
        expected_log_msg_2 = "already runnning: test_package"

        # 結果定義,関数実行
        threads = [threading.Thread(target=_worker) for _ in range(2)]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()

        # 結果評価
        # キャプチャされたログメッセージを取得
        captured_logs = caplog.text

        assert expected_log_msg_1 in captured_logs
        assert expected_log_msg_2 in captured_logs


