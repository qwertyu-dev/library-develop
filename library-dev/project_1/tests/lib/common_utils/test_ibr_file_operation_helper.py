"""テスト実施方法

$ pwd
/developer/library_dev/project_1

# pytest結果をファイル出力する場合
$ pytest -lv ./tests/lib/common_utils/test_ibr_csv_helper.py > tests/log/pytest_result.log

# pytest結果を標準出力する場合
$ pytest -lv ./tests/lib/common_utils/test_ibr_csv_helper.py
"""
import platform
import re
import stat
from pathlib import Path
from unittest.mock import MagicMock

import pytest
from src.lib.common_utils.ibr_enums import LogLevel

#####################################################################
# テスト対象モジュール import, project ディレクトリから起動する
#####################################################################
from src.lib.common_utils.ibr_file_operation_helper import (
    _precheck_read_file,
    _precheck_write_file,
    copy_file,
    delete_file,
    move_file,
    rename_file,
)

#####################################################################
# テスト実行環境セットアップ
#####################################################################
from src.lib.common_utils.ibr_get_config import Config

package_path = Path(__file__)
config = Config.load(package_path)

log_msg = config.log_message
log_msg(str(config), LogLevel.DEBUG)

#####################################################################
# データ作成
#####################################################################
@pytest.fixture(scope='function')
def setup_files(tmp_path) -> (Path, Path):
    # setup
    _dir = tmp_path / "sub"
    _dir.mkdir()
    _file = _dir / "hello.txt"
    _file.write_text("content")

    # テスト実行
    # テスト内で権限をいじる可能性あるため tear downフェーズで戻す
    yield _dir, _file

    # tear down
    # 権限をいろいろいじるので戻す
    # 消してしまっている可能性もあり
    if _file.exists():
        _set_permissions(_file, 0o755)
    if _dir.exists():
        _set_permissions(_dir, 0o755)


# データ作成
@pytest.fixture(scope='function')
def setup_dir(tmp_path) -> (Path, Path):
    # setup
    _dir = tmp_path / "sub"

    # テスト実行
    # テスト内で権限をいじる可能性あるため tear downフェーズで戻す
    yield _dir

    # tear down
    # 権限をいろいろいじるので戻す
    # 消してしまっている可能性もあり
    if _dir.exists():
        _set_permissions(_dir, 0o755)


def _set_permissions(path, permissions) -> None:
    """UNIX系、Windows系の権限設定差異を吸収するテスト用のヘルパー関数"""
    system = platform.system()
    if system == 'Windows':
        # Windows環境特有の話
        # Windowsではwin32securityモジュールを使用
        import ntsecuritycon as con
        import win32security
        sd = win32security.GetFileSecurity(path, win32security.DACL_SECURITY_INFORMATION)
        user, _, _ = win32security.LookupAccountName("", win32security.GetUserName())
        acl = sd.GetSecurityDescriptorDacl()
        if permissions & stat.S_IRUSR:
            acl.AddAccessAllowedAce(win32security.ACL_REVISION, con.FILE_GENERIC_READ, user)
        else:
            acl.AddAccessDeniedAce(win32security.ACL_REVISION, con.FILE_GENERIC_READ, user)
        win32security.SetFileSecurity(path, win32security.DACL_SECURITY_INFORMATION, sd)
    elif system in ('Linux', 'Darwin'):
        # UNIX系のシステムではPath.chmodを使用
        path.chmod(permissions)
    else:
        raise NotImplementedError(f"Unsupported system: {system}") # noqa: EM102 f-stringに変数を許容


class Test__precheck_read_file:
    """_precheck_read_fileのテスト全体をまとめたClass

    C0: 命令カバレッジ
        - 通常読み取り可能
        - 指定ファイルなし
        - 指定ファイルに読み取り権限なし
    C1: 分岐カバレッジ  # C0で検証済
    C2: 条件カバレッジ  # C0で検証済
    """
    def test__precheck_read_file_UT_C0_normal_case(
        self,
        setup_files,
        ) -> None:
        # テスト定義ログ出力はこのまま書いてください、改修不要
        test_doc = """
        - テスト定義:
                - テストカテゴリ: C0
                - テスト区分: 正常系/UT
                - テストシナリオ: ファイル読み込み権限チェック一式
                - ファイル読み取り権限あり状態
        """
        test_functions = [func for func in dir(self) if callable(getattr(self, func)) and func.startswith('test')]
        func_info = f"        - テスト関数: {', '.join(test_functions)}"
        log_msg(f"\n{func_info}{test_doc}", LogLevel.DEBUG)

        # テスト記述
        dir_path, file_path = setup_files
        log_msg(f'target_dir : {dir_path}', LogLevel.DEBUG)
        log_msg(f'target_file : {file_path}', LogLevel.DEBUG)

        # 結果定義,関数実行

        # 結果評価
        # 読み取り権限ありファイル、正常ケース
        assert _precheck_read_file(file_path) is True

        # ディレクトリを指定
        assert _precheck_read_file(dir_path) is False

        # 存在しないファイルを指定
        assert _precheck_read_file(Path('non_exists_file.txt')) is False


    def test__precheck_read_file_UT_C0_non_exist_file(
        self,
        setup_files,
        ) -> None:
        # テスト定義ログ出力はこのまま書いてください、改修不要
        test_doc = """
        - テスト定義:
                - テストカテゴリ: C0
                - テスト区分: 正常系/UT
                - テストシナリオ: ファイル読み込み権限チェック一式
                - ファイルが存在しない
        """
        test_functions = [func for func in dir(self) if callable(getattr(self, func)) and func.startswith('test')]
        func_info = f"        - テスト関数: {', '.join(test_functions)}"
        log_msg(f"\n{func_info}{test_doc}", LogLevel.DEBUG)

        # テスト記述
        dir_path, file_path = setup_files
        log_msg(f'target_dir : {dir_path}', LogLevel.DEBUG)
        log_msg(f'target_file : {file_path}', LogLevel.DEBUG)

        # 結果評価
        # 読み取り権限ありファイル、正常ケース
        assert _precheck_read_file(Path('not exist file')) is False


    def test__precheck_read_file_UT_C0_no_read_priviledges(
        self,
        setup_files,
        ) -> None:
        # テスト定義ログ出力はこのまま書いてください、改修不要
        test_doc = """
        - テスト定義:
                - テストカテゴリ: C0
                - テスト区分: 正常系/UT
                - テストシナリオ: 指定ファイルの読み取り権限チェック
                - ファイル読み取り権限なし状態
                    指定ファイルに読み取り権限剥奪,書き込み取り権限だけ付与状態
                    この設定により書き込み権限はあってもファイル読み取りはできませんので
                    テストでの検証設定を満たすことになります
        """
        test_functions = [func for func in dir(self) if callable(getattr(self, func)) and func.startswith('test')]
        func_info = f"        - テスト関数: {', '.join(test_functions)}"
        log_msg(f"\n{func_info}{test_doc}", LogLevel.DEBUG)

        # テスト記述
        dir_path, file_path = setup_files
        log_msg(f'target_dir : {dir_path}', LogLevel.DEBUG)
        log_msg(f'target_file : {file_path}', LogLevel.DEBUG)

        # 結果評価
        # 指定ファイルに読み取り権限剥奪,書き込み取り権限だけ付与状態
        # file onwerにのみ書き込み権限を設定
        _set_permissions(file_path, 0o200)
        assert _precheck_read_file(file_path) is False


class Test__precheck_write_file:
    """_precheck_write_fileのテスト全体をまとめたClass

    C0: 命令カバレッジ
        - 通常書き込み可能
        - 指定ディレクトリなし
        - 指定ディレクトリ書き込み権限なし
    C1: 分岐カバレッジ  # C0で検証済
    C2: 条件カバレッジ  # C0で検証済
    """
    def test__precheck_write_file_UT_C0_normal_case(
        self,
        setup_files,
        ) -> None:
        # テスト定義ログ出力はこのまま書いてください、改修不要
        test_doc = """
        - テスト定義:
                - テストカテゴリ: C0
                - テスト区分: 正常系/UT
                - テストシナリオ: ディレクトリ書き込み込み権限チェック一式
                - ディレクトリ書き込み権限あり状態
        """
        test_functions = [func for func in dir(self) if callable(getattr(self, func)) and func.startswith('test')]
        func_info = f"        - テスト関数: {', '.join(test_functions)}"
        log_msg(f"\n{func_info}{test_doc}", LogLevel.DEBUG)

        # テスト記述
        dir_path, _ = setup_files
        log_msg(f'target_dir : {dir_path}', LogLevel.DEBUG)

        # 結果定義,関数実行

        # 結果評価
        # ディレクトリあり,ディレクトリ書き込み権限あり,正常ケース
        valid_dir = dir_path / 'valid'
        valid_dir.mkdir()
        assert _precheck_write_file(valid_dir) is True

        # 指定ディレクトリが存在しない
        no_exist_dir = dir_path / 'non_exist_dir'
        assert _precheck_write_file(no_exist_dir) is False


    def test__precheck_write_file_UT_C0_dir_permission_error(
        self,
        setup_files,
        ) -> None:
        # テスト定義ログ出力はこのまま書いてください、改修不要
        test_doc = """
        - テスト定義:
                - テストカテゴリ: C0
                - テスト区分: 正常系/UT
                - テストシナリオ: ディレクトリ書き込み込み権限チェック一式
                - ディレクトリ存在するがディレクトリ書き込み権限なし
        """
        test_functions = [func for func in dir(self) if callable(getattr(self, func)) and func.startswith('test')]
        func_info = f"        - テスト関数: {', '.join(test_functions)}"
        log_msg(f"\n{func_info}{test_doc}", LogLevel.DEBUG)

        # テスト記述
        dir_path, _ = setup_files
        log_msg(f'target_dir : {dir_path}', LogLevel.DEBUG)

        # 結果定義,関数実行

        # 結果評価
        # ディレクトリあり,ディレクトリ書き込み権限あり,正常ケース
        valid_dir = dir_path / 'valid'
        valid_dir.mkdir()
        _set_permissions(valid_dir, 0o444)
        assert _precheck_write_file(valid_dir) is False


class Test_delete_file:
    """deleteのテスト全体をまとめたClass

    C0: 命令カバレッジ
        - ファイルが存在しない、ファイルはあるが読み取り権限なし
        - ファイルが存在しファイル読み取り権限あり
        - Exceptionが発生する
    C1: 分岐カバレッジ  # C0で検証済
    C2: 条件カバレッジ  # C0で検証済
    """
    def test_delete_file_UT_C0_not_exist_file(
        self,
        mocker:MagicMock,
        caplog: pytest.LogCaptureFixture,
        capfd: pytest.LogCaptureFixture,
        setup_files,
        ) -> None:
        # テスト定義ログ出力はこのまま書いてください、改修不要
        test_doc = """
        - テスト定義:
                - テストカテゴリ: C0
                - テスト区分: 正常系/UT
                - テストシナリオ: ファイルが存在しない
                - False検出する
        """
        test_functions = [func for func in dir(self) if callable(getattr(self, func)) and func.startswith('test')]
        func_info = f"        - テスト関数: {', '.join(test_functions)}"
        log_msg(f"\n{func_info}{test_doc}", LogLevel.DEBUG)

        # caplogを使ってログメッセージをキャプチャ
        caplog.set_level(LogLevel.ERROR.value)

        # 期待されるログメッセージ
        expected_log_msg = "指定ファイルが存在しません"

        # テスト記述
        dir_path, _ = setup_files
        log_msg(f'target_dir : {dir_path}', LogLevel.DEBUG)

        # 結果定義,関数実行

        # 結果評価
        # ディレクトリあり,ディレクトリ書き込み権限あり,正常ケース
        non_exist_file = dir_path / 'non_exist_file.txt'
        rc = delete_file(non_exist_file)

        # キャプチャされたログメッセージを取得
        captured_logs = caplog.text

        # ログメッセージが期待通りのものか確認
        assert rc is False
        assert expected_log_msg in captured_logs


    def test_delete_file_UT_C0_no_read_priviledges(
        self,
        mocker:MagicMock,
        caplog: pytest.LogCaptureFixture,
        capfd: pytest.LogCaptureFixture,
        setup_files,
        ) -> None:
        # テスト定義ログ出力はこのまま書いてください、改修不要
        test_doc = """
        - テスト定義:
                - テストカテゴリ: C0
                - テスト区分: 正常系/UT
                - テストシナリオ: ファイルが存在するが読み込み権限なし
                - False検出する
        """
        test_functions = [func for func in dir(self) if callable(getattr(self, func)) and func.startswith('test')]
        func_info = f"        - テスト関数: {', '.join(test_functions)}"
        log_msg(f"\n{func_info}{test_doc}", LogLevel.DEBUG)

        # caplogを使ってログメッセージをキャプチャ
        caplog.set_level(LogLevel.ERROR.value)

        # 期待されるログメッセージ
        expected_log_msg = "指定ファイルに読み取り権限がありません"

        # テスト記述
        dir_path, _ = setup_files
        log_msg(f'target_dir : {dir_path}', LogLevel.DEBUG)

        # 結果定義,関数実行

        # 結果評価
        # ディレクトリあり,ディレクトリ書き込み権限あり,正常ケース
        no_permission_file = dir_path / 'no_permission_file.txt'
        no_permission_file.touch()
        _set_permissions(no_permission_file,0o200)
        rc = delete_file(no_permission_file)

        # キャプチャされたログメッセージを取得
        captured_logs = caplog.text

        # ログメッセージが期待通りのものか確認
        assert rc is False
        assert expected_log_msg in captured_logs


    def test_delete_file_UT_C0_normal_case(
        self,
        setup_files,
        ) -> None:
        # テスト定義ログ出力はこのまま書いてください、改修不要
        test_doc = """
        - テスト定義:
                - テストカテゴリ: C0
                - テスト区分: 正常系/UT
                - テストシナリオ: ファイルが存在し読み込み込み権限あり
                - False検出する
        """
        test_functions = [func for func in dir(self) if callable(getattr(self, func)) and func.startswith('test')]
        func_info = f"        - テスト関数: {', '.join(test_functions)}"
        log_msg(f"\n{func_info}{test_doc}", LogLevel.DEBUG)

        # テスト記述
        dir_path, _ = setup_files
        log_msg(f'target_dir : {dir_path}', LogLevel.DEBUG)

        # 結果定義,関数実行

        # 結果評価
        # ディレクトリあり,ディレクトリ書き込み権限あり,正常ケース
        valid_file = dir_path / 'valid.txt'
        valid_file.touch()
        assert delete_file(valid_file) is True


    def test_delete_file_UT_C0_exception(
        self,
        mocker:MagicMock,
        caplog: pytest.LogCaptureFixture,
        capfd: pytest.LogCaptureFixture,
        setup_files,
        ) -> None:
        # テスト定義ログ出力はこのまま書いてください、改修不要
        test_doc = """
        - テスト定義:
                - テストカテゴリ: C0
                - テスト区分: 正常系/UT
                - テストシナリオ: ファイルが存在し読み込み込み権限あり
                - False検出する
        """
        test_functions = [func for func in dir(self) if callable(getattr(self, func)) and func.startswith('test')]
        func_info = f"        - テスト関数: {', '.join(test_functions)}"
        log_msg(f"\n{func_info}{test_doc}", LogLevel.DEBUG)

        # テスト記述
        dir_path, file_path = setup_files
        log_msg(f'target_dir : {dir_path}', LogLevel.DEBUG)

        # caplogを使ってログメッセージをキャプチャ
        caplog.set_level(LogLevel.ERROR.value)

        # 期待されるログメッセージ
        expected_log_msg = "Traceback"

        # mocker差し替え
        mocker.patch('pathlib.Path.unlink', side_effect=Exception)

        # 結果定義,関数実行

        # 結果評価
        with pytest.raises(Exception):
            assert delete_file(file_path) is True

        # キャプチャされたログメッセージを取得
        captured_logs = caplog.text

        # ログメッセージが期待通りのものか確認
        assert expected_log_msg in captured_logs

class Test_move_file:
    """move_fileのテスト全体をまとめたClass

    C0: 命令カバレッジ
        - 変更元ファイルに読み取り権限がない
        - 変更先ディレクトリに書き込み権限がない
        - 変更先ディレクトリに変更元ファイルと同名のファイルが存在する
        - 前提条件を満たしファイル移動を実施
        - 前提条件を満たしファイル移動を実施した際に例外発生
    C1: 分岐カバレッジ
        - overwrite != 0の場合
    C2: 条件カバレッジ  # C0で検証済
    """
    def test_move_file_UT_C0_no_read_priviledges(
        self,
        mocker:MagicMock,
        caplog: pytest.LogCaptureFixture,
        capfd: pytest.LogCaptureFixture,
        setup_files,
        ) -> None:
        # テスト定義ログ出力はこのまま書いてください、改修不要
        test_doc = """
        - テスト定義:
                - テストカテゴリ: C0
                - テスト区分: 正常系/UT
                - テストシナリオ: ファイルが存在するが読み込み権限なし
                - False検出する
        """
        test_functions = [func for func in dir(self) if callable(getattr(self, func)) and func.startswith('test')]
        func_info = f"        - テスト関数: {', '.join(test_functions)}"
        log_msg(f"\n{func_info}{test_doc}", LogLevel.DEBUG)

        # caplogを使ってログメッセージをキャプチャ
        caplog.set_level(LogLevel.ERROR.value)

        # 期待されるログメッセージ
        expected_log_msg = "指定ファイルに読み取り権限がありません"

        # テスト記述
        dir_path, file_path = setup_files
        log_msg(f'target_dir : {dir_path}', LogLevel.DEBUG)

        # 結果定義,関数実行
        target_dir = dir_path / 'test'
        target_dir.mkdir()

        # 結果評価
        # ディレクトリあり,ディレクトリ読み込み権限あり、ファイル読み取り権限なし
        _set_permissions(file_path, 0o200)
        rc, _new_file_path = move_file(
            file_path,
            target_dir,
            )

        # キャプチャされたログメッセージを取得
        captured_logs = caplog.text

        # ログメッセージが期待通りのものか確認
        assert rc is False
        assert expected_log_msg in captured_logs
        if isinstance(_new_file_path, Path):
            assert _new_file_path.exists() is True
        assert (target_dir / file_path.name).exists() is False
        if file_path.exists():
            _set_permissions(file_path, 0o700)
        assert file_path.exists() is True  # ファイルは移動していない


    def test_move_file_UT_C0_no_write_dir_priviledges(
        self,
        mocker:MagicMock,
        caplog: pytest.LogCaptureFixture,
        capfd: pytest.LogCaptureFixture,
        setup_files,
        ) -> None:
        # テスト定義ログ出力はこのまま書いてください、改修不要
        test_doc = """
        - テスト定義:
                - テストカテゴリ: C0
                - テスト区分: 正常系/UT
                - テストシナリオ: ファイルが存在するがディレクトリ書き込み権限なし
                - False検出する
        """
        test_functions = [func for func in dir(self) if callable(getattr(self, func)) and func.startswith('test')]
        func_info = f"        - テスト関数: {', '.join(test_functions)}"
        log_msg(f"\n{func_info}{test_doc}", LogLevel.DEBUG)

        # caplogを使ってログメッセージをキャプチャ
        caplog.set_level(LogLevel.ERROR.value)

        # 期待されるログメッセージ
        expected_log_msg = "指定ディレクトリに書き込み権限がありません"

        # テスト記述
        dir_path, file_path = setup_files
        log_msg(f'target_dir : {dir_path}', LogLevel.DEBUG)

        # 結果定義,関数実行
        target_dir = dir_path / 'test'
        target_dir.mkdir()

        # 結果評価
        # ディレクトリあり,ディレクトリ書き込み権限なし
        _set_permissions(target_dir, 0o500)
        rc, _new_file_path = move_file(
            file_path,
            target_dir,
            )

        # キャプチャされたログメッセージを取得
        captured_logs = caplog.text

        # ログメッセージが期待通りのものか確認
        assert rc is False
        assert expected_log_msg in captured_logs
        if isinstance(_new_file_path, Path):
            assert _new_file_path.exists() is True
        assert (target_dir / file_path.name).exists() is False
        if file_path.exists():
            _set_permissions(file_path, 0o700)
        assert file_path.exists() is True  # ファイルは移動していない,


    def test_move_file_UT_C0_same_file_exist_to_dir_path(
        self,
        mocker:MagicMock,
        caplog: pytest.LogCaptureFixture,
        capfd: pytest.LogCaptureFixture,
        setup_files,
        ) -> None:
        # テスト定義ログ出力はこのまま書いてください、改修不要
        test_doc = """
        - テスト定義:
                - テストカテゴリ: C0
                - テスト区分: 正常系/UT
                - テストシナリオ: 指定先ディレクトリに同じ名前でファイルが存在する
                - False検出する
        """
        test_functions = [func for func in dir(self) if callable(getattr(self, func)) and func.startswith('test')]
        func_info = f"        - テスト関数: {', '.join(test_functions)}"
        log_msg(f"\n{func_info}{test_doc}", LogLevel.DEBUG)

        # caplogを使ってログメッセージをキャプチャ
        caplog.set_level(LogLevel.ERROR.value)

        # 期待されるログメッセージ
        expected_log_msg = "同じ名前のファイルが存在しています"

        # テスト記述
        dir_path, file_path = setup_files
        log_msg(f'target_dir : {dir_path}', LogLevel.DEBUG)

        # 結果定義,関数実行
        target_dir = dir_path / 'test'
        target_dir.mkdir()
        target_file_name = file_path.name
        target_file_path = target_dir / target_file_name
        target_file_path.touch()

        # 結果評価
        # ターゲットディレクトリにすでに同じ名前のファイルあり
        rc, _new_file_path = move_file(
            file_path,
            target_dir,
            )

        # キャプチャされたログメッセージを取得
        captured_logs = caplog.text

        # ログメッセージが期待通りのものか確認
        assert rc is False
        assert expected_log_msg in captured_logs
        if isinstance(_new_file_path, Path):
            assert _new_file_path.exists() is True
        assert (target_dir / file_path.name).exists() is True  # 同一ファイル名がもともと存在する
        if file_path.exists():
            _set_permissions(file_path, 0o700)
        assert file_path.exists() is True  # ファイルは移動していない


    def test_move_file_UT_C0_normal_case(
        self,
        mocker:MagicMock,
        caplog: pytest.LogCaptureFixture,
        capfd: pytest.LogCaptureFixture,
        setup_files,
        ) -> None:
        # テスト定義ログ出力はこのまま書いてください、改修不要
        test_doc = """
        - テスト定義:
                - テストカテゴリ: C0
                - テスト区分: 正常系/UT
                - テストシナリオ: 指定先ディレクトリに同じ名前でファイルが存在しない
                - ファイル移動可能、正常終了を検出する
        """
        test_functions = [func for func in dir(self) if callable(getattr(self, func)) and func.startswith('test')]
        func_info = f"        - テスト関数: {', '.join(test_functions)}"
        log_msg(f"\n{func_info}{test_doc}", LogLevel.DEBUG)

        # caplogを使ってログメッセージをキャプチャ
        caplog.set_level(LogLevel.INFO.value)

        # 期待されるログメッセージ
        expected_log_msg = "に移動しました"

        # テスト記述
        dir_path, file_path = setup_files
        log_msg(f'target_dir : {dir_path}', LogLevel.DEBUG)

        # 結果定義,関数実行
        target_dir = dir_path / 'test'
        target_dir.mkdir()

        # 結果評価
        # ターゲットディレクトリにすでに同じ名前のファイルあり
        rc, _new_file_path = move_file(
            file_path,
            target_dir,
            )

        # キャプチャされたログメッセージを取得
        captured_logs = caplog.text

        # ログメッセージが期待通りのものか確認
        assert rc is True
        assert expected_log_msg in captured_logs
        if isinstance(_new_file_path, Path):
            assert _new_file_path.exists() is True
        assert (target_dir / file_path.name).exists() is True
        if file_path.exists():
            _set_permissions(file_path, 0o700)
        assert file_path.exists() is False  # ファイルは移動した


    def test_move_file_UT_C0_raise_exception(
        self,
        mocker:MagicMock,
        caplog: pytest.LogCaptureFixture,
        capfd: pytest.LogCaptureFixture,
        setup_files,
        ) -> None:
        # テスト定義ログ出力はこのまま書いてください、改修不要
        test_doc = """
        - テスト定義:
                - テストカテゴリ: C0
                - テスト区分: 正常系/UT
                - テストシナリオ: 指定先ディレクトリに同じ名前でファイルが存在しない
                - ファイル移動可能、だが例外発生を検出する
        """
        test_functions = [func for func in dir(self) if callable(getattr(self, func)) and func.startswith('test')]
        func_info = f"        - テスト関数: {', '.join(test_functions)}"
        log_msg(f"\n{func_info}{test_doc}", LogLevel.DEBUG)

        # caplogを使ってログメッセージをキャプチャ
        caplog.set_level(LogLevel.ERROR.value)

        # 期待されるログメッセージ
        expected_log_msg = "Traceback"

        # テスト記述
        dir_path, file_path = setup_files
        log_msg(f'target_dir : {dir_path}', LogLevel.DEBUG)

        # 結果定義,関数実行
        target_dir = dir_path / 'test'
        target_dir.mkdir()

        # mocker差し替え
        mocker.patch('pathlib.Path.replace', side_effect=Exception)

        # 結果評価
        with pytest.raises(Exception):
            assert move_file(file_path, target_dir) is True

        # キャプチャされたログメッセージを取得
        captured_logs = caplog.text

        # ログメッセージが期待通りのものか確認
        assert expected_log_msg in captured_logs
        assert (target_dir / file_path.name).exists() is False
        if file_path.exists():
            _set_permissions(file_path, 0o700)
        assert file_path.exists() is True  # ファイルは移動していない


    def test_move_file_UT_C0_same_file_exist_to_dir_path_overwrite_true(
        self,
        mocker:MagicMock,
        caplog: pytest.LogCaptureFixture,
        capfd: pytest.LogCaptureFixture,
        setup_files,
        ) -> None:
        # テスト定義ログ出力はこのまま書いてください、改修不要
        test_doc = """
        - テスト定義:
                - テストカテゴリ: C1
                - テスト区分: 正常系/UT
                - テストシナリオ: 指定先ディレクトリに同じ名前でファイルが存在する
                - overwrite可能とする設定
                - True検出する
        """
        test_functions = [func for func in dir(self) if callable(getattr(self, func)) and func.startswith('test')]
        func_info = f"        - テスト関数: {', '.join(test_functions)}"
        log_msg(f"\n{func_info}{test_doc}", LogLevel.DEBUG)

        # caplogを使ってログメッセージをキャプチャ
        caplog.set_level(LogLevel.INFO.value)

        # 期待されるログメッセージ
        expected_log_msg = "に移動しました"

        # テスト記述
        dir_path, file_path = setup_files
        log_msg(f'target_dir : {dir_path}', LogLevel.DEBUG)

        # 結果定義,関数実行
        target_dir = dir_path / 'test'
        target_dir.mkdir()
        target_file_name = file_path.name
        target_file_path = target_dir / target_file_name
        target_file_path.touch()

        # 結果評価
        # ターゲットディレクトリにすでに同じ名前のファイルあり
        rc, _new_file_path = move_file(
            file_path,
            target_dir,
            overwrite=True,
            )

        # キャプチャされたログメッセージを取得
        captured_logs = caplog.text

        # ログメッセージが期待通りのものか確認
        assert rc is True
        assert expected_log_msg in captured_logs
        if isinstance(_new_file_path, Path):
            assert _new_file_path.exists() is True
        assert (target_dir / file_path.name).exists() is True
        if file_path.exists():
            _set_permissions(file_path, 0o700)
        assert file_path.exists() is False  # ファイルは移動していない


class Test_rename_file:
    """rename_fileのテスト全体をまとめたClass

    C0: 命令カバレッジ
        - 変更元ファイルに読み取り権限がない
        - リネーム操作ディレクトリに書き込み権限がない
        - 変更先ディレクトリに変更元ファイルと同名のファイルが存在する
        - 前提条件を満たしファイル移動を実施
        - 前提条件を満たしファイル移動を実施するが例外発生
    C1: 分岐カバレッジ
        - overwrite != 0の場合
    C2: 条件カバレッジ  # C0で検証済
    """
    def test_rename_file_UT_C0_no_read_priviledges(
        self,
        mocker:MagicMock,
        caplog: pytest.LogCaptureFixture,
        capfd: pytest.LogCaptureFixture,
        setup_files,
        ) -> None:
        # テスト定義ログ出力はこのまま書いてください、改修不要
        test_doc = """
        - テスト定義:
                - テストカテゴリ: C0
                - テスト区分: 正常系/UT
                - テストシナリオ: ファイルが存在するが読み込み権限なし
                - False検出する
        """
        test_functions = [func for func in dir(self) if callable(getattr(self, func)) and func.startswith('test')]
        func_info = f"        - テスト関数: {', '.join(test_functions)}"
        log_msg(f"\n{func_info}{test_doc}", LogLevel.DEBUG)

        # caplogを使ってログメッセージをキャプチャ
        caplog.set_level(LogLevel.ERROR.value)

        # 期待されるログメッセージ
        expected_log_msg = "指定ファイルに読み取り権限がありません"

        # テスト記述
        dir_path, file_path = setup_files
        log_msg(f'target_dir : {dir_path}', LogLevel.DEBUG)

        # 結果定義,関数実行
        new_file_name = 'new_file_name.txt'

        # 結果評価
        # ディレクトリあり,ディレクトリ読み込み権限あり、ファイル読み取り権限なし
        _set_permissions(file_path, 0o200)
        rc, _new_file_path = rename_file(
            file_path,
            new_file_name,
            )

        # キャプチャされたログメッセージを取得
        captured_logs = caplog.text

        # ログメッセージが期待通りのものか確認
        assert rc is False
        assert expected_log_msg in captured_logs
        if isinstance(_new_file_path, Path):
            assert _new_file_path.exists() is True
        if file_path.exists():
            _set_permissions(file_path, 0o700)
        assert file_path.exists() is True  # ファイルはリネームしていない


    def test_rename_file_UT_C0_no_write_dir_priviledges(
        self,
        mocker:MagicMock,
        caplog: pytest.LogCaptureFixture,
        capfd: pytest.LogCaptureFixture,
        setup_files,
        ) -> None:
        # テスト定義ログ出力はこのまま書いてください、改修不要
        test_doc = """
        - テスト定義:
                - テストカテゴリ: C0
                - テスト区分: 正常系/UT
                - テストシナリオ: ファイルが存在するがディレクトリ書き込み権限なし
                - False検出する
        """
        test_functions = [func for func in dir(self) if callable(getattr(self, func)) and func.startswith('test')]
        func_info = f"        - テスト関数: {', '.join(test_functions)}"
        log_msg(f"\n{func_info}{test_doc}", LogLevel.DEBUG)

        # caplogを使ってログメッセージをキャプチャ
        caplog.set_level(LogLevel.ERROR.value)

        # 期待されるログメッセージ
        expected_log_msg = "指定ディレクトリに書き込み権限がありません"

        # テスト記述
        dir_path, file_path = setup_files
        log_msg(f'target_dir : {dir_path}', LogLevel.DEBUG)

        # 結果定義,関数実行
        new_file_name = 'new_file_name.txt'

        # 結果評価
        # ディレクトリあり,ディレクトリ書き込み権限なし
        # 読み取りあり、実行ありだが書き込みだけなしにする必要ありなので留意
        _set_permissions(dir_path, 0o500)
        rc, _new_file_path = rename_file(
            file_path,
            new_file_name,
            )

        # キャプチャされたログメッセージを取得
        captured_logs = caplog.text

        # ログメッセージが期待通りのものか確認
        assert rc is False
        assert expected_log_msg in captured_logs
        if isinstance(_new_file_path, Path):
            assert _new_file_path.exists() is True
        if file_path.exists():
            _set_permissions(file_path, 0o700)
        assert file_path.exists() is True  # ファイルはリネームしていない


    def test_rename_file_UT_C0_same_file_exist_to_dir_path(
        self,
        mocker:MagicMock,
        caplog: pytest.LogCaptureFixture,
        capfd: pytest.LogCaptureFixture,
        setup_files,
        ) -> None:
        # テスト定義ログ出力はこのまま書いてください、改修不要
        test_doc = """
        - テスト定義:
                - テストカテゴリ: C0
                - テスト区分: 正常系/UT
                - テストシナリオ: リネーム操作ディレクトリに同じ名前でファイルが存在する
                - リネーム元と同じファイル名を与える
                - False検出する
        """
        test_functions = [func for func in dir(self) if callable(getattr(self, func)) and func.startswith('test')]
        func_info = f"        - テスト関数: {', '.join(test_functions)}"
        log_msg(f"\n{func_info}{test_doc}", LogLevel.DEBUG)

        # caplogを使ってログメッセージをキャプチャ
        caplog.set_level(LogLevel.ERROR.value)

        # 期待されるログメッセージ
        expected_log_msg = "同じ名前のファイルが存在しています"

        # テスト記述
        dir_path, file_path = setup_files
        log_msg(f'target_dir : {dir_path}', LogLevel.DEBUG)

        # 結果定義,関数実行
        target_file_name = file_path.name

        # 結果評価
        # ターゲットディレクトリにすでに同じ名前のファイルあり
        rc, _new_file_path = rename_file(
            file_path,
            target_file_name,
            )

        # キャプチャされたログメッセージを取得
        captured_logs = caplog.text

        # ログメッセージが期待通りのものか確認
        assert rc is False
        assert expected_log_msg in captured_logs
        if isinstance(_new_file_path, Path):
            assert _new_file_path.exists() is True
        if file_path.exists():
            _set_permissions(file_path, 0o700)
        assert file_path.exists() is True  # ファイルはリネームしていない


    def test_rename_file_UT_C0_normal_case(
        self,
        mocker:MagicMock,
        caplog: pytest.LogCaptureFixture,
        capfd: pytest.LogCaptureFixture,
        setup_files,
        ) -> None:
        # テスト定義ログ出力はこのまま書いてください、改修不要
        test_doc = """
        - テスト定義:
                - テストカテゴリ: C0
                - テスト区分: 正常系/UT
                - テストシナリオ: 指定先ディレクトリに同じ名前でファイルが存在しない
                - ファイルリネーム可能、正常終了を検出する
        """
        test_functions = [func for func in dir(self) if callable(getattr(self, func)) and func.startswith('test')]
        func_info = f"        - テスト関数: {', '.join(test_functions)}"
        log_msg(f"\n{func_info}{test_doc}", LogLevel.DEBUG)

        # caplogを使ってログメッセージをキャプチャ
        caplog.set_level(LogLevel.INFO.value)

        # 期待されるログメッセージ
        expected_log_msg = "に変更しました"

        # テスト記述
        dir_path, file_path = setup_files
        log_msg(f'target_dir : {dir_path}', LogLevel.DEBUG)

        # 結果定義,関数実行
        new_file_name = 'new_file_name.txt'

        # 結果評価
        # ターゲットディレクトリにすでに同じ名前のファイルあり
        rc, _new_file_path = rename_file(
            file_path,
            new_file_name,
            )

        # キャプチャされたログメッセージを取得
        captured_logs = caplog.text

        # ログメッセージが期待通りのものか確認
        assert rc is True
        assert expected_log_msg in captured_logs
        if isinstance(_new_file_path, Path):
            assert _new_file_path.exists() is True
        if file_path.exists():
            _set_permissions(file_path, 0o700)
        assert file_path.exists() is False  # ファイルはリネームした


    def test_rename_file_UT_C0_raise_exception(
        self,
        mocker:MagicMock,
        caplog: pytest.LogCaptureFixture,
        capfd: pytest.LogCaptureFixture,
        setup_files,
        ) -> None:
        # テスト定義ログ出力はこのまま書いてください、改修不要
        test_doc = """
        - テスト定義:
                - テストカテゴリ: C0
                - テスト区分: 正常系/UT
                - テストシナリオ: 指定先ディレクトリに同じ名前でファイルが存在しない
                - ファイル移動可能、だが例外発生を検出する
        """
        test_functions = [func for func in dir(self) if callable(getattr(self, func)) and func.startswith('test')]
        func_info = f"        - テスト関数: {', '.join(test_functions)}"
        log_msg(f"\n{func_info}{test_doc}", LogLevel.DEBUG)

        # caplogを使ってログメッセージをキャプチャ
        caplog.set_level(LogLevel.ERROR.value)

        # 期待されるログメッセージ
        expected_log_msg = "Traceback"

        # テスト記述
        dir_path, file_path = setup_files
        log_msg(f'target_dir : {dir_path}', LogLevel.DEBUG)

        # 結果定義,関数実行
        new_file_name = 'new_file_name.txt'

        # mocker差し替え
        mocker.patch('pathlib.Path.rename', side_effect=Exception)

        # 結果評価
        # ターゲットディレクトリにすでに同じ名前のファイルあり
        with pytest.raises(Exception):
            assert rename_file(file_path, new_file_name) is True

        # キャプチャされたログメッセージを取得
        captured_logs = caplog.text

        # ログメッセージが期待通りのものか確認
        assert expected_log_msg in captured_logs
        if file_path.exists():
            _set_permissions(file_path, 0o700)
        assert file_path.exists() is True  # ファイルはリネームしていない


    def test_rename_file_UT_C0_same_file_exist_to_dir_path_overwrite_true(
        self,
        mocker:MagicMock,
        caplog: pytest.LogCaptureFixture,
        capfd: pytest.LogCaptureFixture,
        setup_files,
        ) -> None:
        # テスト定義ログ出力はこのまま書いてください、改修不要
        test_doc = """
        - テスト定義:
                - テストカテゴリ: C1
                - テスト区分: 正常系/UT
                - テストシナリオ: リネーム操作ディレクトリに同じ名前でファイルが存在する
                - overwrite可能とする設定
                - True検出する
        """
        test_functions = [func for func in dir(self) if callable(getattr(self, func)) and func.startswith('test')]
        func_info = f"        - テスト関数: {', '.join(test_functions)}"
        log_msg(f"\n{func_info}{test_doc}", LogLevel.DEBUG)

        # caplogを使ってログメッセージをキャプチャ
        caplog.set_level(LogLevel.INFO.value)

        # 期待されるログメッセージ
        expected_log_msg = "に変更しました"

        # テスト記述
        dir_path, file_path = setup_files
        log_msg(f'target_dir : {dir_path}', LogLevel.DEBUG)

        # 結果定義,関数実行
        new_file_name = file_path.name

        # 結果評価
        # リネーム操作ディレクトリにすでに同じ名前のファイルあり
        rc, _new_file_path = rename_file(
            file_path,
            new_file_name,
            overwrite=True,
            )

        # キャプチャされたログメッセージを取得
        captured_logs = caplog.text

        # ログメッセージが期待通りのものか確認
        assert rc is True
        assert expected_log_msg in captured_logs
        if isinstance(_new_file_path, Path):
            assert _new_file_path.exists() is True
        if file_path.exists():
            _set_permissions(file_path, 0o700)
        assert file_path.exists() is True  # ファイルはリネームしたが同じファイル名なのでTrue


class Test_copy_file:
    """copy_fileのテスト全体をまとめたClass

    C0: 命令カバレッジ
        - with_timestamp == 0,overwrite == 0,正常コピー(paramはデフォルト)
        - with_timestamp != 0,overwrite == 0,正常コピー(with_timestampのみ指定)
        - 変更元ファイルに読み取り権限がない
        - リネーム操作ディレクトリに書き込み権限がない
        - 変更先ディレクトリに変更元ファイルと同名のファイルが存在する(paramはデフォルト)
        - 前提条件を満たしファイルコピーを実施するが例外発生
    C1: 分岐カバレッジ
        - パラメータは全て明示する
            - with_timestamp == 0,overwrite == 0の場合 # C0で検証済
            - with_timestamp != 0,overwrite == 0の場合 # C0で検証済
            - with_timestamp == 0,overwrite != 0の場合,同一ファイル名があり上書きする
            - with_timestamp != 0,overwrite != 0の場合,同一ファイル名があり上書きする
    C2: 条件カバレッジ  # C0で検証済
    """
    def test_copy_file_UT_C0_normal_case(
        self,
        mocker:MagicMock,
        caplog: pytest.LogCaptureFixture,
        capfd: pytest.LogCaptureFixture,
        setup_files,
        ) -> None:
        # テスト定義ログ出力はこのまま書いてください、改修不要
        test_doc = """
        - テスト定義:
                - テストカテゴリ: C0
                - テスト区分: 正常系/UT
                - テストシナリオ: 指定先ディレクトリに同じ名前でファイルが存在しない
                - パラメータはデフォルト値
                - ファイルコピー可能、正常終了を検出する
        """
        test_functions = [func for func in dir(self) if callable(getattr(self, func)) and func.startswith('test')]
        func_info = f"        - テスト関数: {', '.join(test_functions)}"
        log_msg(f"\n{func_info}{test_doc}", LogLevel.DEBUG)

        # caplogを使ってログメッセージをキャプチャ
        caplog.set_level(LogLevel.INFO.value)

        # 期待されるログメッセージ
        expected_log_msg = "にコピーしました"

        # テスト記述
        dir_path, file_path = setup_files
        log_msg(f'target_dir : {dir_path}', LogLevel.DEBUG)

        # 結果定義,関数実行
        target_dir = dir_path / 'test'
        target_dir.mkdir()

        # 結果評価
        rc, _new_file_path = copy_file(
            file_path,
            target_dir,
            )
        log_msg(f'_new_file_path : {_new_file_path.name}', LogLevel.DEBUG)

        # キャプチャされたログメッセージを取得
        captured_logs = caplog.text

        # 生成ファイル名生成
        # 日付因子付与なし
        match = re.search(fr'^{file_path.name}$', str(_new_file_path.name))

        # ログメッセージが期待通りのものか確認
        assert rc is True
        assert expected_log_msg in captured_logs
        assert match is not None
        if isinstance(_new_file_path, Path):
            assert _new_file_path.exists() is True
        if file_path.exists():
            _set_permissions(file_path, 0o700)
        assert file_path.exists() is True  # コピー元は存在する


    def test_copy_file_UT_C0_normal_case_with_timestamp_true_overwrite_true(
        self,
        mocker:MagicMock,
        caplog: pytest.LogCaptureFixture,
        capfd: pytest.LogCaptureFixture,
        setup_files,
        ) -> None:
        # テスト定義ログ出力はこのまま書いてください、改修不要
        test_doc = """
        - テスト定義:
                - テストカテゴリ: C0
                - テスト区分: 正常系/UT
                - テストシナリオ: 指定先ディレクトリに同じ名前でファイルが存在しない
                - パラメータは変更
                    - with_timestamp=True, overwriteはデフォルト
                - ファイルコピー可能、正常終了を検出する
        """
        test_functions = [func for func in dir(self) if callable(getattr(self, func)) and func.startswith('test')]
        func_info = f"        - テスト関数: {', '.join(test_functions)}"
        log_msg(f"\n{func_info}{test_doc}", LogLevel.DEBUG)

        # caplogを使ってログメッセージをキャプチャ
        caplog.set_level(LogLevel.INFO.value)

        # 期待されるログメッセージ
        expected_log_msg = "にコピーしました"

        # テスト記述
        dir_path, file_path = setup_files
        log_msg(f'target_dir : {dir_path}', LogLevel.DEBUG)

        # 結果定義,関数実行
        target_dir = dir_path / 'test'
        target_dir.mkdir()

        # 結果評価
        # タイムスタンプ指定
        rc, _new_file_path = copy_file(
            file_path,
            target_dir,
            with_timestamp=True)

        # キャプチャされたログメッセージを取得
        captured_logs = caplog.text

        # 生成ファイル名生成
        # 日付因子付与あり
        # ファイル名に . を含むためescapeする必要があります
        # {}は正規表現では特殊な意味を持つため、{}自体を文字列に含める場合は{{}}と書く必要があります
        original_filename = re.escape(file_path.name)
        match = re.search(rf'^{original_filename}_(\d{{8}}_\d{{6}})$', _new_file_path.name)

        log_msg(f'file_path.name : {file_path.name}', LogLevel.INFO)
        log_msg(f'original_filename : {original_filename}', LogLevel.INFO)
        log_msg(rf'^{original_filename}_(\d{{8}}_\d{{6}})$', LogLevel.INFO)

        # ログメッセージが期待通りのものか確認
        assert rc is True
        assert expected_log_msg in captured_logs
        assert match is not None
        assert _new_file_path.exists() is True         # ファイルは移動した
        _set_permissions(file_path, 0o700)
        assert file_path.exists() is True  # ファイルは移動した,


    def test_copy_file_UT_C0_no_read_priviledges(
        self,
        mocker:MagicMock,
        caplog: pytest.LogCaptureFixture,
        capfd: pytest.LogCaptureFixture,
        setup_files,
        ) -> None:
        # テスト定義ログ出力はこのまま書いてください、改修不要
        test_doc = """
        - テスト定義:
                - テストカテゴリ: C0
                - テスト区分: 正常系/UT
                - テストシナリオ: 変更元ファイルに読み取り権限がない
                - False検出する
        """
        test_functions = [func for func in dir(self) if callable(getattr(self, func)) and func.startswith('test')]
        func_info = f"        - テスト関数: {', '.join(test_functions)}"
        log_msg(f"\n{func_info}{test_doc}", LogLevel.DEBUG)

        # caplogを使ってログメッセージをキャプチャ
        caplog.set_level(LogLevel.ERROR.value)

        # 期待されるログメッセージ
        expected_log_msg = "指定ファイルに読み取り権限がありません"

        # テスト記述
        dir_path, file_path = setup_files
        log_msg(f'target_dir : {dir_path}', LogLevel.DEBUG)

        # 結果定義,関数実行
        target_dir = dir_path / 'test'
        target_dir.mkdir()

        # 結果評価
        # ディレクトリあり,ディレクトリ読み込み権限あり、ファイル読み取り権限なし
        _set_permissions(file_path, 0o200)
        rc, _new_file_path = copy_file(file_path, target_dir)

        # キャプチャされたログメッセージを取得
        captured_logs = caplog.text

        # ログメッセージが期待通りのものか確認
        assert rc is False
        assert expected_log_msg in captured_logs
        if isinstance(_new_file_path, Path):
            assert _new_file_path.exists() is True
        if file_path.exists():
            _set_permissions(file_path, 0o700)
        assert file_path.exists() is True  # コピー元は存在する


    def test_copy_file_UT_C0_no_write_dir_priviledges(
        self,
        mocker:MagicMock,
        caplog: pytest.LogCaptureFixture,
        capfd: pytest.LogCaptureFixture,
        setup_files,
        ) -> None:
        # テスト定義ログ出力はこのまま書いてください、改修不要
        test_doc = """
        - テスト定義:
                - テストカテゴリ: C0
                - テスト区分: 正常系/UT
                - テストシナリオ: コピー操作ディレクトリに書き込み権限がない
                - False検出する
        """
        test_functions = [func for func in dir(self) if callable(getattr(self, func)) and func.startswith('test')]
        func_info = f"        - テスト関数: {', '.join(test_functions)}"
        log_msg(f"\n{func_info}{test_doc}", LogLevel.DEBUG)

        # caplogを使ってログメッセージをキャプチャ
        caplog.set_level(LogLevel.ERROR.value)

        # 期待されるログメッセージ
        expected_log_msg = "指定ディレクトリに書き込み権限がありません"

        # テスト記述
        dir_path, file_path = setup_files
        log_msg(f'target_dir : {dir_path}', LogLevel.DEBUG)

        # 結果定義,関数実行
        target_dir = dir_path / 'test'
        target_dir.mkdir()

        # 結果評価
        # ディレクトリあり,ディレクトリ書き込み権限なし
        # 読み取りあり、実行ありだが書き込みだけなしにする必要ありなので留意
        _set_permissions(target_dir, 0o500)
        rc, _new_file_path = copy_file(file_path, target_dir)

        # キャプチャされたログメッセージを取得
        captured_logs = caplog.text

        # ログメッセージが期待通りのものか確認
        assert rc is False
        assert expected_log_msg in captured_logs
        if isinstance(_new_file_path, Path):
            assert _new_file_path.exists() is True  # ファイルはコピーした
        _set_permissions(file_path, 0o700)
        assert file_path.exists() is True  # コピー元は存在する


    def test_copy_file_UT_C0_same_file_exist_to_dir_path(
        self,
        mocker:MagicMock,
        caplog: pytest.LogCaptureFixture,
        capfd: pytest.LogCaptureFixture,
        setup_files,
        ) -> None:
        # テスト定義ログ出力はこのまま書いてください、改修不要
        test_doc = """
        - テスト定義:
                - テストカテゴリ: C0
                - テスト区分: 正常系/UT
                - テストシナリオ: コピー先ディレクトリに同じ名前でファイルが存在する
                - リネーム元と同じファイル名を与える
                - False検出する
        """
        test_functions = [func for func in dir(self) if callable(getattr(self, func)) and func.startswith('test')]
        func_info = f"        - テスト関数: {', '.join(test_functions)}"
        log_msg(f"\n{func_info}{test_doc}", LogLevel.DEBUG)

        # caplogを使ってログメッセージをキャプチャ
        caplog.set_level(LogLevel.ERROR.value)

        # 期待されるログメッセージ
        expected_log_msg = "同じ名前のファイルが存在しています"

        # テスト記述
        dir_path, file_path = setup_files
        log_msg(f'target_dir : {dir_path}', LogLevel.DEBUG)

        # 結果定義,関数実行
        target_dir = dir_path / 'test'
        target_dir.mkdir()
        target_file_name = file_path.name
        target_file_path = target_dir / target_file_name
        target_file_path.touch()

        # 結果評価
        # ターゲットディレクトリにすでに同じ名前のファイルあり
        rc, _new_file_path = rename_file(file_path, target_dir)

        # キャプチャされたログメッセージを取得
        captured_logs = caplog.text

        # ログメッセージが期待通りのものか確認
        assert rc is False
        assert expected_log_msg in captured_logs
        if isinstance(_new_file_path, Path):
            assert _new_file_path.exists() is True # ファイルはコピーした
        _set_permissions(file_path, 0o700)
        assert file_path.exists() is True  # コピー元は存在する


    def test_copy_file_UT_C0_raise_exception(
        self,
        mocker:MagicMock,
        caplog: pytest.LogCaptureFixture,
        capfd: pytest.LogCaptureFixture,
        setup_files,
        ) -> None:
        # テスト定義ログ出力はこのまま書いてください、改修不要
        test_doc = """
        - テスト定義:
                - テストカテゴリ: C0
                - テスト区分: 正常系/UT
                - テストシナリオ: 指定先ディレクトリに同じ名前でファイルが存在しない
                - ファイル移動可能、だが例外発生を検出する
        """
        test_functions = [func for func in dir(self) if callable(getattr(self, func)) and func.startswith('test')]
        func_info = f"        - テスト関数: {', '.join(test_functions)}"
        log_msg(f"\n{func_info}{test_doc}", LogLevel.DEBUG)

        # caplogを使ってログメッセージをキャプチャ
        caplog.set_level(LogLevel.ERROR.value)

        # 期待されるログメッセージ
        expected_log_msg = "Traceback"

        # テスト記述
        dir_path, file_path = setup_files
        log_msg(f'target_dir : {dir_path}', LogLevel.DEBUG)

        # 結果定義,関数実行
        target_dir = dir_path / 'test'
        target_dir.mkdir()

        # mocker差し替え
        mocker.patch('shutil.copy2', side_effect=Exception)

        # 結果評価
        # ターゲットディレクトリにすでに同じ名前のファイルあり
        with pytest.raises(Exception):
            assert copy_file(file_path, target_dir) is True

        # キャプチャされたログメッセージを取得
        captured_logs = caplog.text

        # ログメッセージが期待通りのものか確認
        assert expected_log_msg in captured_logs
        _set_permissions(file_path, 0o700)
        assert file_path.exists() is True  # コピー元は存在する


    def test_copy_file_UT_C1_same_file_exist_to_dir_path_overrite_true(
        self,
        mocker:MagicMock,
        caplog: pytest.LogCaptureFixture,
        capfd: pytest.LogCaptureFixture,
        setup_files,
        ) -> None:
        # テスト定義ログ出力はこのまま書いてください、改修不要
        test_doc = """
        - テスト定義:
                - テストカテゴリ: C1
                - テスト区分: 正常系/UT
                - テストシナリオ: コピー先ディレクトリに同じ名前でファイルが存在する
                - リネーム元と同じファイル名を与える
                - with_timestamp == 0,overwrite != 0の場合,同一ファイル名があり上書きする
                - True検出する
        """
        test_functions = [func for func in dir(self) if callable(getattr(self, func)) and func.startswith('test')]
        func_info = f"        - テスト関数: {', '.join(test_functions)}"
        log_msg(f"\n{func_info}{test_doc}", LogLevel.DEBUG)

        # caplogを使ってログメッセージをキャプチャ
        caplog.set_level(LogLevel.INFO.value)

        # 期待されるログメッセージ
        expected_log_msg = "コピーしました"

        # テスト記述
        dir_path, file_path = setup_files
        log_msg(f'target_dir : {dir_path}', LogLevel.DEBUG)

        # 結果定義,関数実行
        target_dir = dir_path / 'test'
        target_dir.mkdir()
        target_file_name = file_path.name
        target_file_path = target_dir / target_file_name
        target_file_path.touch()

        # 結果評価
        # ターゲットディレクトリにすでに同じ名前のファイルあり
        rc, _new_file_path = copy_file(
            file_path,
            target_dir,
            overwrite=True,
            )

        # キャプチャされたログメッセージを取得
        captured_logs = caplog.text

        # 日付因子付与あり
        # ファイル名に . を含むためescapeする必要があります
        # {}は正規表現では特殊な意味を持つため、{}自体を文字列に含める場合は{{}}と書く必要があります
        original_filename = re.escape(file_path.name)
        match = re.search(rf'^{original_filename}$', _new_file_path.name)

        log_msg(f'file_path.name : {file_path.name}', LogLevel.INFO)
        log_msg(f'original_filename : {original_filename}', LogLevel.INFO)
        log_msg(rf'^{original_filename}$', LogLevel.INFO)

        # ログメッセージが期待通りのものか確認
        assert rc is True
        assert expected_log_msg in captured_logs
        assert match is not None
        if isinstance(_new_file_path, Path):
            assert _new_file_path.exists() is True # ファイルは移動した
        _set_permissions(file_path, 0o700)
        assert file_path.exists() is True  # コピー元は存在する


    def test_copy_file_UT_C1_same_file_exist_to_dir_path_overrite_true_with_timestamp_true(
        self,
        mocker:MagicMock,
        caplog: pytest.LogCaptureFixture,
        capfd: pytest.LogCaptureFixture,
        setup_files,
        ) -> None:
        # テスト定義ログ出力はこのまま書いてください、改修不要
        test_doc = """
        - テスト定義:
                - テストカテゴリ: C1
                - テスト区分: 正常系/UT
                - テストシナリオ: コピー先ディレクトリに同じ名前でファイルが存在する
                - リネーム元と同じファイル名を与える
                - with_timestamp == 0,overwrite != 0の場合,同一ファイル名があり上書きする
                - True検出する
        """
        test_functions = [func for func in dir(self) if callable(getattr(self, func)) and func.startswith('test')]
        func_info = f"        - テスト関数: {', '.join(test_functions)}"
        log_msg(f"\n{func_info}{test_doc}", LogLevel.DEBUG)

        # caplogを使ってログメッセージをキャプチャ
        caplog.set_level(LogLevel.INFO.value)

        # 期待されるログメッセージ
        expected_log_msg = "コピーしました"

        # テスト記述
        dir_path, file_path = setup_files
        log_msg(f'target_dir : {dir_path}', LogLevel.DEBUG)

        # 結果定義,関数実行
        target_dir = dir_path / 'test'
        target_dir.mkdir()
        target_file_name = file_path.name
        target_file_path = target_dir / target_file_name
        target_file_path.touch()

        # 結果評価
        # ターゲットディレクトリにすでに同じ名前のファイルあり
        rc, _new_file_path = copy_file(
            file_path,
            target_dir,
            overwrite=True,
            with_timestamp=True,
            )

        # キャプチャされたログメッセージを取得
        captured_logs = caplog.text

        # 日付因子付与あり
        # ファイル名に . を含むためescapeする必要があります
        # {}は正規表現では特殊な意味を持つため、{}自体を文字列に含める場合は{{}}と書く必要があります
        original_filename = re.escape(file_path.name)
        match = re.search(rf'^{original_filename}_(\d{{8}}_\d{{6}})$', _new_file_path.name)

        log_msg(f'file_path.name : {file_path.name}', LogLevel.INFO)
        log_msg(f'original_filename : {original_filename}', LogLevel.INFO)
        log_msg(rf'^{original_filename}_(\d{{8}}_\d{{6}})$', LogLevel.INFO)

        # ログメッセージが期待通りのものか確認
        assert rc is True
        assert expected_log_msg in captured_logs
        assert match is not None
        if isinstance(_new_file_path, Path):
            assert _new_file_path.exists() is True # ファイルはコピーした
        _set_permissions(file_path, 0o700)
        assert file_path.exists() is True  # コピー元は存在する

