"""テスト実施方法

# project topディレクトリから実行する
$ pwd
/developer/library_dev/project_1

# pytest結果をファイル出力する場合
$ pytest -lv ./tests/lib/common_utils/test_ibr_csv_helper.py > tests/log/pytest_result.log

# pytest結果を標準出力する場合
$ pytest -lv ./tests/lib/common_utils/test_ibr_csv_helper.py
"""
import logging
from pathlib import Path
from unittest.mock import MagicMock

import pytest
import os
import toml

#####################################################################
# テスト実行環境セットアップ
#####################################################################
from src.lib.common_utils.ibr_enums import (
    ExecEnvironment,
    LogLevel,
)

#####################################################################
# テスト対象モジュール import, project ディレクトリから起動する
#####################################################################
from src.lib.common_utils.ibr_logger_package import (
    LoggerPackage,
    SingletonType,
)

# このテストはConfig自体がテスト対象という事案

#####################################################################
# データ作成
#####################################################################
@pytest.fixture(scope='function')
def create_config(tmp_path: Path) -> (Path, Path):
    """データ作成処理

    tomlファイル作成

    Args:
        tmp_path (Path): データ出力先

    Returns:
        Path: 作成したデータへのpath common_config.toml
        Path: 作成したデータへのpath package_config.toml
    """
    # setup
    os.environ.get('EXEC_PATTERN', 'src')
    # テスト用のcommon_config.tomlとpackage_config.tomlの内容を準備
    test_common_config = {
        'local': {
            'logger_path': {
                'LOGGER_DEF_FILE': 'test_logging.json',
                'LOGGER_MSG_FILE': 'test_message.toml',
            },
            'input_file_path': {
                'UPDATE_EXCEL_PATH': 'test_receive',
            },
            'output_file_path': {
                'SEND_REFERENCE_MASTER_PATH': 'test_send',
            },
        },
    }
    test_package_config = {
        'local': {
            'some_package_setting': 'value',
        },
    }
    file_path_common = tmp_path / 'test_file_1.toml'
    with file_path_common.open(mode='w') as f:
        toml.dump(test_common_config, f)

    file_path_package = tmp_path / 'test_file_2.toml'
    with file_path_package.open(mode='w') as f:
        toml.dump(test_package_config, f)

    return file_path_common, file_path_package

    # 実行
    #yield

    # tear down
    # Notes:
    #   pytestのtmp系はデフォルトで3セッションのみ維持します
    #   従ってtear downでtmp利用資源は明示削除は必須ではありません

@pytest.fixture(scope='function')
def create_empty_config(tmp_path: Path) -> (Path, Path):
    """データ作成処理

    tomlファイル作成

    Args:
        tmp_path (Path): データ出力先

    Returns:
        Path: 作成したデータへのpath common_config.toml
    """
    # setup
    # テスト用のcommon_config.tomlとpackage_config.tomlの内容を準備
    test_common_config = { }
    test_package_config = { }
    file_path_common = tmp_path / 'test_file_3.toml'
    with file_path_common.open(mode='w') as f:
        toml.dump(test_common_config, f)

    file_path_package = tmp_path / 'test_file_4.toml'
    with file_path_package.open(mode='w') as f:
        toml.dump(test_package_config, f)

    return file_path_common, file_path_package

    # 実行
    #yield

    # tear down
    # Notes:
    #   pytestのtmp系はデフォルトで3セッションのみ維持します
    #   従ってtear downでtmp利用資源は明示削除は必須ではありません


@pytest.fixture(scope='function')
def _reset_singleton_instance() -> None:
    # シングルトンインスタンスをリセット
    SingletonType.reset_instances()
    yield
    # 念のためテスト後にもリセット
    SingletonType.reset_instances()


class Test_singleton_type:
    """ibr_logger_packageのSingletonTypeクラスのテスト全体をまとめたClass

    このテストはlogger機能自体のテストであることから
    標準出力にはprint文を使用することを許容する
    print文でのassertが必要な場合はcapdf fixtureを使用すること

    C0: 命令カバレッジ
        - SingletonTypeからのインスタンスを生成,型及びinstance確認
        - Singleton機能確認、インスタンスを複数生成しても同一インスタンスであること
    C1: 分岐カバレッジ # C0テストで検証済
    C2: 条件カバレッジ # C0テストで検証済
    """

    def test_singleton_call_UT_C0_instance_checks(
        self,
        create_config: (Path, Path),
        ) -> None:
        # テスト定義ログ出力はこのまま書いてください、改修不要
        test_doc = """
        - テスト定義:
                - テストカテゴリ: C0
                - テスト区分: 正常系/UT
                - テストシナリオ: インスタンス生成,メタクラスがSingletonTypeとなっている
                - インスタンス複数生成しても同一インスタンスである
        """
        test_functions = [func for func in dir(self) if callable(getattr(self, func)) and func.startswith('test')]
        func_info = f"        - テスト関数: {', '.join(test_functions)}"
        print(f"\n{func_info}{test_doc}")

        # SingletonTypeをメタクラスとして持つClassを定義
        class TestClass(metaclass=SingletonType):
            pass

        # TestClassインスタンスを作成
        # おなじTestClassインスタンスを生成
        instance1 = TestClass()
        instance2 = TestClass()

        # インスタンス生成型確認
        assert isinstance(TestClass, SingletonType)
        assert isinstance(instance1, TestClass)

        # 両方のインスタンスが同じであることを確認
        # シングルトンの特性
        assert instance1 == instance2


class Test_loggerpackage:
    """ibr_logger_packageのLoggerPackageクラスのテスト全体をまとめたClass

    このテストはlogger機能自体のテストであることから
    標準出力にはprint文を使用することを許容する
    print文でのassertが必要な場合はcapdf fixtureを使用すること

    C0: 命令カバレッジ
        - SingletonTypeからのインスタンスを生成,型及びinstance確認
    C1: 分岐カバレッジ
        - 各ローカルメソッドの検証に委ねる,このテストでは実施しない
    C2: 条件カバレッジ
        - 各ローカルメソッドの検証に委ねる,このテストでは実施しない
    """

    def test_loggerpackage_UT_C0_create_instance_normal(
        self,
        create_config: (Path, Path),
        ) -> None:
        # テスト定義ログ出力はこのまま書いてください、改修不要
        test_doc = """
        - テスト定義:
                - テストカテゴリ: C0
                - テスト区分: 正常系/UT
                - テストシナリオ: インスタンス生成,メタクラスがSingletonTypeとなっている
                - __init__処理結果により取得した情報確認
                - インスタンス複数生成しても同一インスタンスである
        """
        test_functions = [func for func in dir(self) if callable(getattr(self, func)) and func.startswith('test')]
        func_info = f"        - テスト関数: {', '.join(test_functions)}"
        print(f"\n{func_info}{test_doc}")

        # TestClassインスタンスを作成
        # おなじTestClassインスタンスを生成
        test_instance1 = LoggerPackage(__file__)
        test_instance1.log_message('IBRDEV-I-0000001')  # MSGテーブルキーヒット
        test_instance1.log_message('test test test')    # MSGテーブルキーヒットなし, LogLevel.INFO(デフォルト)
        test_instance1.log_message('test test test', LogLevel.ERROR)    # MSGテーブルキーヒットなし, LogLevel.ERROR

        # インスタンス生成型確認
        assert isinstance(LoggerPackage, SingletonType)
        assert isinstance(test_instance1, LoggerPackage)

        # __init__処理時の取得情報確認
        expected_log_msg1 = 'logging_TimedRotate.json'
        expected_log_msg2 = 'config_MessageList.toml'
        assert expected_log_msg1 in str(test_instance1.LOGGER_DEF_FILE), f"Traceback '{expected_log_msg1}' to be in captured logs, but it was not.'"
        assert expected_log_msg2 in str(test_instance1.LOGGER_MSG_FILE), f"Traceback '{expected_log_msg2}' to be in captured logs, but it was not.'"
        assert isinstance(test_instance1._logger, logging.Logger)  # noqa: SLF001 testのため_資源へのアクセスを許容
        assert isinstance(test_instance1._message_table, dict)

        # おなじTestClassインスタンスを生成
        test_instance2 = LoggerPackage(__file__)

        # 両方のインスタンスが同じであることを確認
        # シングルトンの特性
        assert test_instance1 == test_instance2


class Test_loggerpackage__init__tests:
    """ibr_logger_packageのLoggerPackageクラス__init__メソッドのテスト全体をまとめたClass

    このテストはlogger機能自体のテストであることから
    標準出力にはprint文を使用することを許容する
    print文でのassertが必要な場合はcapdf fixtureを使用すること

    インスタンス生成時に渡す識別子の結果srcと判断するケースは別テストに切り出して実施する
    このテストはtestsと判断するケースをベースとして全てのテストを実施する。

    srcと判別されるケースは以下のテストコードで実施する
        - See. test_ibr_logger_package_src__Init__.py


    C0: 命令カバレッジ
        - 正常生成  # class Test_loggerpackageで実施済
        - インスタンス変数への格納
            - self._name
            - self._exec_pattern
        - Exception
    C1: 分岐カバレッジ
        - インスタンス生成時の引数に srcを含まない # C0で検証済
        - インスタンス生成時の引数に srcを含む
    C2: 条件カバレッジ
    """
    # モジュールのファイルパスで環境判定する仕様から
    #  OSの環境変数でsrc or testsを判定する仕様に変更となっている
    # 従って以下２ケースはその役割を終えているため、実施不要
    #
    #def test_loggerpackage_init_UT_C0_tests_path(
    #    self,
    #    _reset_singleton_instance,
    #    create_config: (Path, Path),
    #    ) -> None:
    #    # テスト定義ログ出力はこのまま書いてください、改修不要
    #    test_doc = """
    #    - テスト定義:
    #            - テストカテゴリ: C0
    #            - テスト区分: 正常系/UT
    #            - テストシナリオ: インスタンス生成,メタクラスがSingletonTypeとなっている
    #            - __init__処理結果により取得した情報確認
    #            - 環境判別として 'tests'を採択するケース
    #    """
    #    test_functions = [func for func in dir(self) if callable(getattr(self, func)) and func.startswith('test')]
    #    func_info = f"        - テスト関数: {', '.join(test_functions)}"
    #    print(f"\n{func_info}{test_doc}")

    #    # TestClassインスタンスを作成
    #    test_instance1 = LoggerPackage(__file__)

    #    assert test_instance1._name == 'test_ibr_logger_package.py'  # noqa: SLF001 testのため_資源へのアクセスを許容
    #    assert test_instance1._exec_pattern == 'tests'               # noqa: SLF001 testのため_資源へのアクセスを許容


    #def test_loggerpackage_init_UT_C1_src_path(
    #    self,
    #    _reset_singleton_instance,
    #    create_config: (Path, Path),
    #    ) -> None:
    #    # テスト定義ログ出力はこのまま書いてください、改修不要
    #    test_doc = """
    #    - テスト定義:
    #            - テストカテゴリ: C1
    #            - テスト区分: 正常系/UT
    #            - テストシナリオ: インスタンス生成,メタクラスがSingletonTypeとなっている
    #            - __init__処理結果により取得した情報確認
    #            - 環境判別として 'src'を採択するケース
    #    """
    #    test_functions = [func for func in dir(self) if callable(getattr(self, func)) and func.startswith('test')]
    #    func_info = f"        - テスト関数: {', '.join(test_functions)}"
    #    print(f"\n{func_info}{test_doc}")

    #    test_path = 'src/nanigashi/aaa.py'
    #    test_instance2 = LoggerPackage(test_path)

    #    assert test_instance2._name == 'aaa.py'  # noqa: SLF001 testのため_資源へのアクセスを許容
    #    assert test_instance2._exec_pattern == 'src'               # noqa: SLF001 testのため_資源へのアクセスを許容


    def test_loggerpackage_init_UT_C0_raise_exception(
        self,
        mocker:MagicMock,
        caplog: pytest.LogCaptureFixture,
        capfd: pytest.LogCaptureFixture,
        _reset_singleton_instance,
        ) -> None:
        # テスト定義ログ出力はこのまま書いてください、改修不要
        test_doc = """
        - テスト定義:
                - テストカテゴリ: C0
                - テスト区分: 正常系/UT
                - テストシナリオ: 例外発生
                - raise SystemExit
        """
        test_functions = [func for func in dir(self) if callable(getattr(self, func)) and func.startswith('test')]
        func_info = f"        - テスト関数: {', '.join(test_functions)}"
        print(f"\n{func_info}{test_doc}")

        # 期待されるstderrメッセージ
        expected_sysout_msg = 'Config生成に失敗しました'

        # PythonのEnumクラスでは__members__属性は読み取り専用のmappingproxyオブジェクトであり
        # 直接モックすることはできません。
        # しかし、Enumクラス自体をモックすることで、__members__属性を操作することが可能です。
        mock_enum = mocker.patch('src.lib.common_utils.ibr_logger_package.LoggerPackage._get_exec_env', autospec=True)
        mock_enum.__members__ = MagicMock()
        mock_enum.__members__.get.side_effect = Exception()

        with pytest.raises(SystemExit):
            logger_package = LoggerPackage('dummy_patch')
            _ = logger_package._get_enum_value(ExecEnvironment, 'DEBUG', 'default')
            captured = capfd.readouterr()

            print(captured.out)
            assert expected_sysout_msg in captured.out


class Test_loggerpackage__get_enum_value:
    """ibr_logger_packageのLoggerPackageクラス_get_enum_valueメソッドのテスト全体をまとめたClass

    このテストはlogger機能自体のテストであることから
    標準出力にはprint文を使用することを許容する
    print文でのassertが必要な場合はcapdf fixtureを使用すること

    C0: 命令カバレッジ
        - EnumをKey検索しValueを取得する
        - EnumをKey検索するがヒットせず、指定したdefault値を取得する
        - 例外発生
    C1: 分岐カバレッジ
        - 存在しないEnumを指定する
        - Keyを指定しない
        - default値を指定しない
    C2: 条件カバレッジ
    """
    def test_loggerpackage_get_enum_value_UT_C0_local(
        self,
        mocker:MagicMock,
        caplog: pytest.LogCaptureFixture,
        capfd: pytest.LogCaptureFixture,
        _reset_singleton_instance,
        ) -> None:
        # テスト定義ログ出力はこのまま書いてください、改修不要
        test_doc = """
        - テスト定義:
                - テストカテゴリ: C0
                - テスト区分: 正常系/UT
                - テストシナリオ: Loglevel enumを使用してKey検索する
                - テストシナリオ: Loglevel enumを使用してKey検索するがKeyヒットせずデフォルト指定値が返る

        """
        test_functions = [func for func in dir(self) if callable(getattr(self, func)) and func.startswith('test')]
        func_info = f"        - テスト関数: {', '.join(test_functions)}"
        print(f"\n{func_info}{test_doc}")

        logger_package = LoggerPackage('dummy_patch')
        # 各Enum検索を実行
        enum_value_DEBUG = logger_package._get_enum_value(LogLevel, 'DEBUG', 'default')
        enum_value_INFO = logger_package._get_enum_value(LogLevel, 'INFO', 'default')
        enum_value_WARNING = logger_package._get_enum_value(LogLevel, 'WARNING', 'default')
        enum_value_ERROR = logger_package._get_enum_value(LogLevel, 'ERROR', 'default')
        enum_value_CRITICAL = logger_package._get_enum_value(LogLevel, 'CRITICAL', 'default')

        # キーヒットしない場合はDefault設定が返る
        enum_value_default = logger_package._get_enum_value(LogLevel, 'xxxx', ExecEnvironment.HOSTNAME_LOCAL )

        # .valueが戻ってくるので評価値には留意で
        assert enum_value_DEBUG == 10
        assert enum_value_INFO == 20
        assert enum_value_WARNING == 30
        assert enum_value_ERROR == 40
        assert enum_value_CRITICAL == 50
        assert enum_value_default == 'local'


    def test_loggerpackage_get_enum_value_UT_C0_raise_exception(
        self,
        mocker:MagicMock,
        caplog: pytest.LogCaptureFixture,
        capfd: pytest.LogCaptureFixture,
        _reset_singleton_instance,
        ) -> None:
        # テスト定義ログ出力はこのまま書いてください、改修不要
        test_doc = """
        - テスト定義:
                - テストカテゴリ: C0
                - テスト区分: 正常系/UT
                - テストシナリオ: 例外発生
                - raise SystemExit
        """
        test_functions = [func for func in dir(self) if callable(getattr(self, func)) and func.startswith('test')]
        func_info = f"        - テスト関数: {', '.join(test_functions)}"
        print(f"\n{func_info}{test_doc}")

        # 期待されるstderrメッセージ
        excepted_sysout_msg = 'Enumからの値取得に失敗しました'

        # PythonのEnumクラスでは__members__属性は読み取り専用のmappingproxyオブジェクトであり
        # 直接モックすることはできません。
        # しかし、Enumクラス自体をモックすることで、__members__属性を操作することが可能です。
        mock_enum = mocker.patch('src.lib.common_utils.ibr_enums.ExecEnvironment', autospec=True)
        mock_enum.__members__ = MagicMock()
        mock_enum.__members__.get.side_effect = Exception()

        with pytest.raises(Exception):  # noqa: PT012 stdout採取による評価のため許容
            logger_package = LoggerPackage('dummy_patch')
            _ = logger_package._get_enum_value(ExecEnvironment, 'DEBUG', 'default')
            captured = capfd.readouterr()

            assert captured.out == excepted_sysout_msg


    def test_loggerpackage_get_enum_value_UT_C1_specify_wrong_enum(
        self,
        mocker:MagicMock,
        caplog: pytest.LogCaptureFixture,
        capfd: pytest.LogCaptureFixture,
        _reset_singleton_instance,
        ) -> None:
        # テスト定義ログ出力はこのまま書いてください、改修不要
        test_doc = """
        - テスト定義:
                - テストカテゴリ: C1
                - テスト区分: 正常系/UT
                - テストシナリオ: 存在しないEnumsを指定
                - raise NameError -> raise SystemExit
        """
        test_functions = [func for func in dir(self) if callable(getattr(self, func)) and func.startswith('test')]
        func_info = f"        - テスト関数: {', '.join(test_functions)}"
        print(f"\n{func_info}{test_doc}")

        # 期待されるstderrメッセージ
        excepted_sysout_msg = 'Enumからの値取得に失敗しました'

        with pytest.raises(NameError):  # noqa: PT012 stdout採取による評価のため許容
            logger_package = LoggerPackage('dummy_patch')
            _ = logger_package._get_enum_value(AAAA, 'DEBUG', 'default')
            captured = capfd.readouterr()

            assert captured.out == excepted_sysout_msg


    def test_loggerpackage_get_enum_value_UT_C1_specify_no_key_param(
        self,
        mocker:MagicMock,
        caplog: pytest.LogCaptureFixture,
        capfd: pytest.LogCaptureFixture,
        _reset_singleton_instance,
        ) -> None:
        # テスト定義ログ出力はこのまま書いてください、改修不要
        test_doc = """
        - テスト定義:
                - テストカテゴリ: C1
                - テスト区分: 正常系/UT
                - テストシナリオ: keyパラメータを書かない
                - TypeError -> raise SystemExit

        """
        test_functions = [func for func in dir(self) if callable(getattr(self, func)) and func.startswith('test')]
        func_info = f"        - テスト関数: {', '.join(test_functions)}"
        print(f"\n{func_info}{test_doc}")

        # 期待されるstderrメッセージ
        excepted_sysout_msg = 'Enumからの値取得に失敗しました'

        with pytest.raises(TypeError):  # noqa: PT012 stdout採取による評価のため許容
            logger_package = LoggerPackage('dummy_patch')
            _ = logger_package._get_enum_value(ExecEnvironment, 'default')
            captured = capfd.readouterr()

            assert captured.out == excepted_sysout_msg


    def test_loggerpackage_get_enum_value_UT_C1_specify_no_default_param(
        self,
        mocker:MagicMock,
        caplog: pytest.LogCaptureFixture,
        capfd: pytest.LogCaptureFixture,
        _reset_singleton_instance,
        ) -> None:
        # テスト定義ログ出力はこのまま書いてください、改修不要
        test_doc = """
        - テスト定義:
                - テストカテゴリ: C1
                - テスト区分: 正常系/UT
                - テストシナリオ: defaultパラメータを書かない
                - TypeError -> raise SystemExit

        """
        test_functions = [func for func in dir(self) if callable(getattr(self, func)) and func.startswith('test')]
        func_info = f"        - テスト関数: {', '.join(test_functions)}"
        print(f"\n{func_info}{test_doc}")

        # 期待されるstderrメッセージ
        excepted_sysout_msg = 'Enumからの値取得に失敗しました'

        with pytest.raises(TypeError):  # noqa: PT012 stdout採取による評価のため許容
            logger_package = LoggerPackage('dummy_patch')
            _ = logger_package._get_enum_value(ExecEnvironment, 'DEBUG')
            captured = capfd.readouterr()

            assert captured.out == excepted_sysout_msg


class Test_loggerpackage__get_exec_env:
    """ibr_logger_packageのLoggerPackageクラス_get_exec_envメソッドのテスト全体をまとめたClass

    このテストはlogger機能自体のテストであることから
    標準出力にはprint文を使用することを許容する
    print文でのassertが必要な場合はcapdf fixtureを使用すること

    C0: 命令カバレッジ
        - local
        - 例外発生
    C1: 分岐カバレッジ
    C2: 条件カバレッジ
        - local        # C0で検証済
        - develop
        - regression
        - production
    """
    def test_loggerpackage_get_exec_env_UT_C0_local(
        self,
        mocker:MagicMock,
        caplog: pytest.LogCaptureFixture,
        capfd: pytest.LogCaptureFixture,
        _reset_singleton_instance,
        ) -> None:
        # テスト定義ログ出力はこのまま書いてください、改修不要
        test_doc = """
        - テスト定義:
                - テストカテゴリ: C0
                - テスト区分: 正常系/UT
                - テストシナリオ: インスタンス生成,メタクラスがSingletonTypeとなっている
                - __get_env_value__処理結果により取得した情報確認
                - 環境判別として 'tests'を採択するケース
        """
        test_functions = [func for func in dir(self) if callable(getattr(self, func)) and func.startswith('test')]
        func_info = f"        - テスト関数: {', '.join(test_functions)}"
        print(f"\n{func_info}{test_doc}")

        mocker.patch('socket.gethostname', return_value='local')
        logger_package = LoggerPackage('dummy_patch')
        assert logger_package._env == 'local'


    def test_loggerpackage_get_exec_env_UT_C0_raise_exception(
        self,
        mocker:MagicMock,
        caplog: pytest.LogCaptureFixture,
        capfd: pytest.LogCaptureFixture,
        _reset_singleton_instance,
        ) -> None:
        # テスト定義ログ出力はこのまま書いてください、改修不要
        test_doc = """
        - テスト定義:
                - テストカテゴリ: C0
                - テスト区分: 正常系/UT
                - テストシナリオ: インスタンス生成,メタクラスがSingletonTypeとなっている
                - __get_env_value__処理結果により取得した情報確認
                - 環境判別として 'tests'を採択するケース
                - raise SystemExit
                - Singleton._instance is {}

                LoggerPackageのインスタンス生成時にExceptionが発生し
                それがSystemExitに変換されることを正しくテストを行う


        """
        test_functions = [func for func in dir(self) if callable(getattr(self, func)) and func.startswith('test')]
        func_info = f"        - テスト関数: {', '.join(test_functions)}"
        print(f"\n{func_info}{test_doc}")

        # 期待されるstderrメッセージ
        excepted_sysout_msg = 'ホスト名の取得に失敗しました'

        mocker.patch('src.lib.common_utils.ibr_logger_package.LoggerPackage._get_enum_value', side_effect=Exception)
        with pytest.raises(SystemExit):  # noqa: PT012 stdout採取による評価のため許容
            assert  LoggerPackage('dummy_patch') is True
            captured = capfd.readouterr()
            assert captured.out == excepted_sysout_msg
            assert SingletonType._instances is {}


    def test_loggerpackage_get_exec_env_UT_C2_develop(
        self,
        mocker:MagicMock,
        caplog: pytest.LogCaptureFixture,
        capfd: pytest.LogCaptureFixture,
        _reset_singleton_instance,
        ) -> None:
        # テスト定義ログ出力はこのまま書いてください、改修不要
        test_doc = """
        - テスト定義:
                - テストカテゴリ: C2
                - テスト区分: 正常系/UT
                - テストシナリオ: インスタンス生成,メタクラスがSingletonTypeとなっている
                - __get_env_value__処理結果により取得した情報確認
                - 環境判別として 'tests'を採択するケース
                - 実行ホスト developを想定
        """
        test_functions = [func for func in dir(self) if callable(getattr(self, func)) and func.startswith('test')]
        func_info = f"        - テスト関数: {', '.join(test_functions)}"
        print(f"\n{func_info}{test_doc}")

        mocker.patch('socket.gethostname', return_value='HOSTNAME_DEVELOP')
        logger_package = LoggerPackage('dummy_patch')
        assert logger_package._env == 'develop'


    # 以下２ケースはサーバドライブPath問題があり
    # ローカルUTでは実施する際にエラーとなる→存在しないドライブ
    #
    #def test_loggerpackage_get_exec_env_UT_C2_regression(
    #    self,
    #    mocker:MagicMock,
    #    caplog: pytest.LogCaptureFixture,
    #    capfd: pytest.LogCaptureFixture,
    #    _reset_singleton_instance,
    #    ) -> None:
    #    # テスト定義ログ出力はこのまま書いてください、改修不要
    #    test_doc = """
    #    - テスト定義:
    #            - テストカテゴリ: C2
    #            - テスト区分: 正常系/UT
    #            - テストシナリオ: インスタンス生成,メタクラスがSingletonTypeとなっている
    #            - __get_env_value__処理結果により取得した情報確認
    #            - 環境判別として 'tests'を採択するケース
    #            - 実行ホスト regressionを想定
    #    """
    #    test_functions = [func for func in dir(self) if callable(getattr(self, func)) and func.startswith('test')]
    #    func_info = f"        - テスト関数: {', '.join(test_functions)}"
    #    print(f"\n{func_info}{test_doc}")

    #    mocker.patch('socket.gethostname', return_value='HOSTNAME_REGRESSION')
    #    logger_package = LoggerPackage('dummy_patch')
    #    assert logger_package._env == 'regression'


    #def test_loggerpackage_get_exec_env_UT_C2_production(
    #    self,
    #    mocker:MagicMock,
    #    caplog: pytest.LogCaptureFixture,
    #    capfd: pytest.LogCaptureFixture,
    #    _reset_singleton_instance,
    #    ) -> None:
    #    # テスト定義ログ出力はこのまま書いてください、改修不要
    #    test_doc = """
    #    - テスト定義:
    #            - テストカテゴリ: C2
    #            - テスト区分: 正常系/UT
    #            - テストシナリオ: インスタンス生成,メタクラスがSingletonTypeとなっている
    #            - __get_env_value__処理結果により取得した情報確認
    #            - 環境判別として 'tests'を採択するケース
    #            - 実行ホスト productionを想定
    #    """
    #    test_functions = [func for func in dir(self) if callable(getattr(self, func)) and func.startswith('test')]
    #    func_info = f"        - テスト関数: {', '.join(test_functions)}"
    #    print(f"\n{func_info}{test_doc}")

    #    mocker.patch('socket.gethostname', return_value='HOSTNAME_PRODUCTION')
    #    logger_package = LoggerPackage('dummy_patch')
    #    assert logger_package._env == 'production'


class Test_loggerpackage_toml_parser:
    """ibr_logger_packageのLoggerPackageクラス _toml_parser メソッドのテスト全体をまとめたClass

    このテストはlogger機能自体のテストであることから
    標準出力にはprint文を使用することを許容する
    print文でのassertが必要な場合はcapdf fixtureを使用すること

    結局は test_ibr_csv_helper.pyのインプットが
    CSVからtomlに変わった程度と同じこと

    C0: 命令カバレッジ
        - ファイルパスをstrで与え,存在する/読み取り権限がある
        - ファイルパスをPathで与え,存在する/読み取り権限がある
        - 例外
            - FileNotFoundError
            - PermissionError
            - IsADirestoryError
            - Exception
    C1: 分岐カバレッジ
    C2: 条件カバレッジ
        - tomlファイルが空
    """
    def test_loggerpackage_toml_perser_specify_str_path(
        self,
        _reset_singleton_instance,
        create_config:(Path, Path),
        ) -> None:
        # テスト定義ログ出力はこのまま書いてください、改修不要
        test_doc = """
        - テスト定義:
                - テストカテゴリ: C0
                - テスト区分: 正常系/UT
                - テストシナリオ: tomlパスを読み込みdictを返す、典型パターン
                - pathをstrで与える
        """
        test_functions = [func for func in dir(self) if callable(getattr(self, func)) and func.startswith('test')]
        func_info = f"        - テスト関数: {', '.join(test_functions)}"
        print(f"\n{func_info}{test_doc}", LogLevel.DEBUG)

        # toml取得
        # strのまま実行
        test_config_toml, test_package_toml = create_config

        # expected
        expected = {'local': {'logger_path': {'LOGGER_DEF_FILE': 'test_logging.json', 'LOGGER_MSG_FILE': 'test_message.toml'}, 'input_file_path': {'UPDATE_EXCEL_PATH': 'test_receive'}, 'output_file_path': {'SEND_REFERENCE_MASTER_PATH': 'test_send'}}}

        # テスト記述
        logger_package = LoggerPackage('dummy_patch')
        result = logger_package._toml_parser(test_config_toml) 

        assert isinstance(result, dict)
        assert result == expected


    def test_loggerpackage_toml_perser_specify_path(
        self,
        _reset_singleton_instance,
        create_config:(Path, Path),
        ) -> None:
        # テスト定義ログ出力はこのまま書いてください、改修不要
        test_doc = """
        - テスト定義:
                - テストカテゴリ: C0
                - テスト区分: 正常系/UT
                - テストシナリオ: tomlパスを読み込みdictを返す、典型パターン
                - pathをstrで与える
        """
        test_functions = [func for func in dir(self) if callable(getattr(self, func)) and func.startswith('test')]
        func_info = f"        - テスト関数: {', '.join(test_functions)}"
        print(f"\n{func_info}{test_doc}", LogLevel.DEBUG)

        # toml取得
        test_config_toml, test_package_toml = create_config

        # Path変換
        test_config_toml = Path(test_config_toml)

        # expected
        expected = {'local': {'logger_path': {'LOGGER_DEF_FILE': 'test_logging.json', 'LOGGER_MSG_FILE': 'test_message.toml'}, 'input_file_path': {'UPDATE_EXCEL_PATH': 'test_receive'}, 'output_file_path': {'SEND_REFERENCE_MASTER_PATH': 'test_send'}}}

        # テスト記述
        logger_package = LoggerPackage('dummy_patch')
        result = logger_package._toml_parser(test_config_toml)

        assert isinstance(result, dict)
        assert result == expected


    def test_loggerpackage_toml_perser_raise_FileNotFoundError(
        self,
        mocker:MagicMock,
        caplog: pytest.LogCaptureFixture,
        capfd: pytest.LogCaptureFixture,
        create_config:(Path, Path),
        ) -> None:
        # テスト定義ログ出力はこのまま書いてください、改修不要
        test_doc = """
        - テスト定義:
                - テストカテゴリ: C0
                - テスト区分: 正常系/UT
                - テストシナリオ: tomlパスを読み込む際にFineNotFound発生,mocker及びside_effectで対応
        """
        test_functions = [func for func in dir(self) if callable(getattr(self, func)) and func.startswith('test')]
        func_info = f"        - テスト関数: {', '.join(test_functions)}"
        print(f"\n{func_info}{test_doc}", LogLevel.DEBUG)

        # toml取得
        test_config_toml, test_package_toml = create_config

        # Path変換
        test_config_toml = Path(test_config_toml)

        # 期待されるログメッセージ
        expected_sysout_msg = "can not get target files "

        # テスト記述
        logger_package = LoggerPackage('dummy_patch')
        mocker.patch('pathlib.Path.open', side_effect=FileNotFoundError)
        with pytest.raises(FileNotFoundError):
            _ =logger_package._toml_parser(test_config_toml) is True
            captured = capfd.readouterr()

            # ログメッセージが期待通りのものか確認
            assert captured.out == expected_sysout_msg


    def test_loggerpackage_toml_perser_raise_PermissionError(
        self,
        mocker:MagicMock,
        caplog: pytest.LogCaptureFixture,
        capfd: pytest.LogCaptureFixture,
        create_config:(Path, Path),
        ) -> None:
        # テスト定義ログ出力はこのまま書いてください、改修不要
        test_doc = """
        - テスト定義:
                - テストカテゴリ: C0
                - テスト区分: 正常系/UT
                - テストシナリオ: tomlパスを読み込む際にPermissionFound発生,mocker及びside_effectで対応
        """
        test_functions = [func for func in dir(self) if callable(getattr(self, func)) and func.startswith('test')]
        func_info = f"        - テスト関数: {', '.join(test_functions)}"
        print(f"\n{func_info}{test_doc}", LogLevel.DEBUG)

        # toml取得
        test_config_toml, test_package_toml = create_config

        # Path変換
        test_config_toml = Path(test_config_toml)

        # 期待されるログメッセージ
        expected_sysout_msg = "No permission to read the file"

        # テスト記述
        logger_package = LoggerPackage('dummy_patch')
        mocker.patch('pathlib.Path.open', side_effect=PermissionError)
        with pytest.raises(PermissionError):
            _ =logger_package._toml_parser(test_config_toml) is True
            captured = capfd.readouterr()

            # ログメッセージが期待通りのものか確認
            assert captured.out == expected_sysout_msg


    def test_loggerpackage_toml_perser_raise_IsADirectoryError(
        self,
        mocker:MagicMock,
        caplog: pytest.LogCaptureFixture,
        capfd: pytest.LogCaptureFixture,
        create_config:(Path, Path),
        ) -> None:
        # テスト定義ログ出力はこのまま書いてください、改修不要
        test_doc = """
        - テスト定義:
                - テストカテゴリ: C0
                - テスト区分: 正常系/UT
                - テストシナリオ: tomlパスを読み込む際にIsADirectory発生,mocker及びside_effectで対応
        """
        test_functions = [func for func in dir(self) if callable(getattr(self, func)) and func.startswith('test')]
        func_info = f"        - テスト関数: {', '.join(test_functions)}"
        print(f"\n{func_info}{test_doc}", LogLevel.DEBUG)

        # toml取得
        test_config_toml, test_package_toml = create_config

        # Path変換
        test_config_toml = Path(test_config_toml)

        # 期待されるログメッセージ
        expected_sysout_msg = "The specified path is a directory, not a file"

        # テスト記述
        logger_package = LoggerPackage('dummy_patch')
        mocker.patch('pathlib.Path.open', side_effect=IsADirectoryError)
        with pytest.raises(IsADirectoryError):
            _ =logger_package._toml_parser(test_config_toml) is True
            captured = capfd.readouterr()

            # ログメッセージが期待通りのものか確認
            assert captured.out == expected_sysout_msg


    def test_loggerpackage_toml_perser_raise_Exception(
        self,
        mocker:MagicMock,
        caplog: pytest.LogCaptureFixture,
        capfd: pytest.LogCaptureFixture,
        create_config:(Path, Path),
        ) -> None:
        # テスト定義ログ出力はこのまま書いてください、改修不要
        test_doc = """
        - テスト定義:
                - テストカテゴリ: C0
                - テスト区分: 正常系/UT
                - テストシナリオ: tomlパスを読み込む際にIsADirectory発生,mocker及びside_effectで対応
        """
        test_functions = [func for func in dir(self) if callable(getattr(self, func)) and func.startswith('test')]
        func_info = f"        - テスト関数: {', '.join(test_functions)}"
        print(f"\n{func_info}{test_doc}", LogLevel.DEBUG)

        # toml取得
        test_config_toml, test_package_toml = create_config

        # Path変換
        test_config_toml = Path(test_config_toml)

        # 期待されるログメッセージ
        expected_sysout_msg = "Traceback"

        # テスト記述
        logger_package = LoggerPackage('dummy_patch')
        mocker.patch('pathlib.Path.open', side_effect=Exception)
        with pytest.raises(Exception):
            _ =logger_package._toml_parser(test_config_toml) is True
            captured = capfd.readouterr()

            # ログメッセージが期待通りのものか確認
            assert captured.out == expected_sysout_msg


    def test_loggerpackage_toml_perser_empty(
        self,
        _reset_singleton_instance,
        create_empty_config:(Path, Path),
        ) -> None:
        # テスト定義ログ出力はこのまま書いてください、改修不要
        test_doc = """
        - テスト定義:
                - テストカテゴリ: C2
                - テスト区分: 正常系/UT
                - テストシナリオ: tomlパスを読み込みdictを返す、典型パターン
                - pathをstrで与える,ただしtomlファイルは空ファイル
        """
        test_functions = [func for func in dir(self) if callable(getattr(self, func)) and func.startswith('test')]
        func_info = f"        - テスト関数: {', '.join(test_functions)}"
        print(f"\n{func_info}{test_doc}", LogLevel.DEBUG)

        # toml取得
        test_config_toml, test_package_toml = create_empty_config

        # Path変換
        test_config_toml = Path(test_config_toml)

        # expected
        expected = {}

        # テスト記述
        logger_package = LoggerPackage('dummy_patch')
        result = logger_package._toml_parser(test_config_toml)

        assert isinstance(result, dict)
        assert result == expected


class Test_loggerpackage_get_config_dict:
    """ibr_logger_packageのLoggerPackageクラス _get_config_dict メソッドのテスト全体をまとめたClass

    このテストはlogger機能自体のテストであることから
    標準出力にはprint文を使用することを許容する
    print文でのassertが必要な場合はcapdf fixtureを使用すること

    C0: 命令カバレッジ
        - 正常実行、toml定義事項がdictとして取得できる
        - 例外
            - Exception
    C1: 分岐カバレッジ
    C2: 条件カバレッジ
    """
    def test_loggerpackage_get_config_dict_normal(
        self,
        _reset_singleton_instance,
        create_config:(Path, Path),
        ) -> None:
        # テスト定義ログ出力はこのまま書いてください、改修不要
        test_doc = """
        - テスト定義:
                - テストカテゴリ: C0
                - テスト区分: 正常系/UT
                - テストシナリオ: dictを返す典型パターン
        """
        test_functions = [func for func in dir(self) if callable(getattr(self, func)) and func.startswith('test')]
        func_info = f"        - テスト関数: {', '.join(test_functions)}"
        print(f"\n{func_info}{test_doc}", LogLevel.DEBUG)

        # toml取得
        # strのまま実行
        test_config_toml, test_package_toml = create_config

        # expected
        expected = {'production': {'logger_path': {'LOGGER_DEF_FILE': 'src/def/ibrUtilsLoggingHelper/logging_TimedRotateServer.json', 'LOGGER_MSG_FILE': 'src/def/ibrUtilsLoggingHelper/config_MessageList.toml'}}, 'regression': {'logger_path': {'LOGGER_DEF_FILE': 'src/def/ibrUtilsLoggingHelper/logging_TimedRotateServer.json', 'LOGGER_MSG_FILE': 'src/def/ibrUtilsLoggingHelper/config_MessageList.toml'}, 'optional_path': {'LONGTERM_ACCUM_PATH': 'W:\\reference\\src\\work\\longterm_accm', 'SHORTTERM_ACCUM_PATH': 'W:\\reference\\src\\work\\shortterm_accm', 'TABLE_PATH': 'Z:\\reference\\src\\table', 'SHARE_RECEIVE_PATH': 'Z:\\reference\\src\\share\\receive', 'SHARE_SEND_PATH': 'Z:\\reference\\src\\share\\send', 'ARCHIVES_REFERNCE_SNAPSHOT_PATH': 'Z:\\reference\\src\\archives\\reference_snapshots', 'ARCHIVES_REQUEST_SNAPSHOT_PATH': 'Z:\\reference\\src\\archives\\request_snapshots', 'ARCHIVES_REFERENCE_DIFFS_PATH': 'Z:\\reference\\src\\archives\\reference_diffs', 'ARCHIVES_CSV_FILES_PATH': 'Z:\\reference\\src\\archives\\csv_files'}}, 'develop': {'logger_path': {'LOGGER_DEF_FILE': 'src/def/ibrUtilsLoggingHelper/logging_TimedRotate.json', 'LOGGER_MSG_FILE': 'src/def/ibrUtilsLoggingHelper/config_MessageList.toml'}}, 'local': {'logger_path': {'LOGGER_DEF_FILE': 'src/def/ibrUtilsLoggingHelper/logging_TimedRotate.json', 'LOGGER_MSG_FILE': 'src/def/ibrUtilsLoggingHelper/config_MessageList.toml'}, 'decision_table_path': {'DECISION_TABLE_PATH': 'src/def/decision_table'}, 'optional_path': {'LONGTERM_ACCUM_PATH': 'src/work/longterm_accm', 'SHORTTERM_ACCUM_PATH': 'src/work/shortterm_accm', 'TABLE_PATH': 'src/table', 'SHARE_RECEIVE_PATH': 'src/share/receive', 'SHARE_SEND_PATH': 'src/share/send', 'ARCHIVES_REFERNCE_SNAPSHOT_PATH': 'src/archives/reference_snapshots', 'ARCHIVES_REQUEST_SNAPSHOT_PATH': 'src/archives/request_snapshots', 'ARCHIVES_REFERENCE_DIFFS_PATH': 'src/archives/reference_diffs', 'ARCHIVES_CSV_FILES_PATH': 'src/archives/csv_files'}}}

        # テスト記述
        logger_package = LoggerPackage('dummy_patch')
        _ = logger_package._get_config_dict()

        assert isinstance(logger_package._common_config, dict)
        assert logger_package._common_config == expected


    def test_loggerpackage_get_config_dict_raise_Exception(
        self,
        mocker:MagicMock,
        caplog: pytest.LogCaptureFixture,
        capfd: pytest.LogCaptureFixture,
        create_config:(Path, Path),
        ) -> None:
        # テスト定義ログ出力はこのまま書いてください、改修不要
        test_doc = """
        - テスト定義:
                - テストカテゴリ: C0
                - テスト区分: 正常系/UT
                - テストシナリオ: tomlパスを読み込む際に例外発生
        """
        test_functions = [func for func in dir(self) if callable(getattr(self, func)) and func.startswith('test')]
        func_info = f"        - テスト関数: {', '.join(test_functions)}"
        print(f"\n{func_info}{test_doc}", LogLevel.DEBUG)

        # toml取得
        test_config_toml, test_package_toml = create_config

        # Path変換
        test_config_toml = Path(test_config_toml)

        # 期待されるログメッセージ
        expected_sysout_msg = "logger定義の取得に失敗しました"

        # テスト記述
        logger_package = LoggerPackage('dummy_patch')
        mocker.patch('pathlib.Path.open', side_effect=Exception)
        with pytest.raises(Exception):
            _ =logger_package._get_config_dict() is True
            captured = capfd.readouterr()

            # ログメッセージが期待通りのものか確認
            assert captured.out == expected_sysout_msg


class Test_loggerpackage_create_logger:
    """ibr_logger_packageのLoggerPackageクラス _create_loggerメソッドのテスト全体をまとめたClass

    このテストはlogger機能自体のテストであることから
    標準出力にはprint文を使用することを許容する
    print文でのassertが必要な場合はcapdf fixtureを使用すること

    logger定義のパスはcommon_config.toml内に定義されている

    C0: 命令カバレッジ
        - 正常実行、logger生成される
        - 例外
            - Exception
    C1: 分岐カバレッジ
    C2: 条件カバレッジ
    """
    def test_loggerpackage_create_logger_normal(
        self,
        _reset_singleton_instance,
        create_config:(Path, Path),
        ) -> None:
        # テスト定義ログ出力はこのまま書いてください、改修不要
        test_doc = """
        - テスト定義:
                - テストカテゴリ: C0
                - テスト区分: 正常系/UT
                - テストシナリオ: loggerを返す典型パターン
                    - 型確認
                    - logger.nameが引数指定文字列と一致
        """
        test_functions = [func for func in dir(self) if callable(getattr(self, func)) and func.startswith('test')]
        func_info = f"        - テスト関数: {', '.join(test_functions)}"
        print(f"\n{func_info}{test_doc}", LogLevel.DEBUG)

        # toml取得
        # strのまま実行
        test_config_toml, test_package_toml = create_config

        # テスト記述
        logger_package = LoggerPackage('dummy_patch')
        _ = logger_package._create_logger()

        assert isinstance(logger_package._logger, logging.Logger)
        assert logger_package._logger.name == 'dummy_patch'


    def test_loggerpackage_create_logger_raise_Exception(
        self,
        mocker:MagicMock,
        caplog: pytest.LogCaptureFixture,
        capfd: pytest.LogCaptureFixture,
        create_config:(Path, Path),
        ) -> None:
        # テスト定義ログ出力はこのまま書いてください、改修不要
        test_doc = """
        - テスト定義:
                - テストカテゴリ: C0
                - テスト区分: 正常系/UT
                - テストシナリオ: tomlパスを読み込む際に例外発生
        """
        test_functions = [func for func in dir(self) if callable(getattr(self, func)) and func.startswith('test')]
        func_info = f"        - テスト関数: {', '.join(test_functions)}"
        print(f"\n{func_info}{test_doc}", LogLevel.DEBUG)

        # toml取得
        test_config_toml, test_package_toml = create_config

        # Path変換
        test_config_toml = Path(test_config_toml)

        # 期待されるログメッセージ
        expected_sysout_msg = "logger定義の生成に失敗しました"

        # テスト記述
        logger_package = LoggerPackage('dummy_patch')
        mocker.patch('pathlib.Path.open', side_effect=Exception)
        with pytest.raises(Exception):
            _ =logger_package._create_logger() is True
            captured = capfd.readouterr()

            # ログメッセージが期待通りのものか確認
            assert captured.out == expected_sysout_msg


class Test_loggerpackage_create_msg_table:
    """ibr_logger_packageのLoggerPackageクラス _create_message_tableメソッドのテスト全体をまとめたClass

    このテストはlogger機能自体のテストであることから
    標準出力にはprint文を使用することを許容する
    print文でのassertが必要な場合はcapdf fixtureを使用すること

    message_table定義のパスはcommon_config.toml内に定義されている

    C0: 命令カバレッジ
        - 正常実行、dict生成される
        - 例外
            - Exception
    C1: 分岐カバレッジ
    C2: 条件カバレッジ
    """
    def test_loggerpackage_create_msg_table_normal(
        self,
        _reset_singleton_instance,
        create_config:(Path, Path),
        ) -> None:
        # テスト定義ログ出力はこのまま書いてください、改修不要
        test_doc = """
        - テスト定義:
                - テストカテゴリ: C0
                - テスト区分: 正常系/UT
                - テストシナリオ: dictを返す典型パターン
                    - 型確認
        """
        test_functions = [func for func in dir(self) if callable(getattr(self, func)) and func.startswith('test')]
        func_info = f"        - テスト関数: {', '.join(test_functions)}"
        print(f"\n{func_info}{test_doc}", LogLevel.DEBUG)

        # toml取得
        # strのまま実行
        test_config_toml, test_package_toml = create_config

        # dict予想値
        expected = {'IBRDEV-I-0000001': '起動しました', 'IBRDEV-I-0000002': '正常終了しました', 'IBRDEV-I-0000003': '定義取得しました', 'IBRDEV-I-0000004': 'Mutexによる多重制御を開始します', 'IBRDEV-I-0000005': 'Mutexによる多重制御を終了しました', 'IBRDEV-E-0000001': '異常終了しました', 'IBRDEV-E-0000100': 'ValidationErrorが発生しました', 'IBRDEV-W-0000001': '何かしら要注意です'}

        # テスト記述
        logger_package = LoggerPackage('dummy_patch')
        _= logger_package._create_msg_table()

        assert isinstance(logger_package._message_table, dict)
        assert expected == logger_package._message_table


    def test_loggerpackage_create_msg_table_raise_Exception(
        self,
        mocker:MagicMock,
        caplog: pytest.LogCaptureFixture,
        capfd: pytest.LogCaptureFixture,
        create_config:(Path, Path),
        ) -> None:
        # テスト定義ログ出力はこのまま書いてください、改修不要
        test_doc = """
        - テスト定義:
                - テストカテゴリ: C0
                - テスト区分: 正常系/UT
                - テストシナリオ: tomlパスを読み込む際に例外発生
        """
        test_functions = [func for func in dir(self) if callable(getattr(self, func)) and func.startswith('test')]
        func_info = f"        - テスト関数: {', '.join(test_functions)}"
        print(f"\n{func_info}{test_doc}", LogLevel.DEBUG)

        # toml取得
        test_config_toml, test_package_toml = create_config

        # Path変換
        test_config_toml = Path(test_config_toml)

        # 期待されるログメッセージ
        expected_sysout_msg = "msg_table定義の生成に失敗しました"

        # テスト記述
        logger_package = LoggerPackage('dummy_patch')
        mocker.patch('pathlib.Path.open', side_effect=Exception)
        with pytest.raises(Exception):
            _ =logger_package._create_msg_table() is True
            captured = capfd.readouterr()

            # ログメッセージが期待通りのものか確認
            assert captured.out == expected_sysout_msg



class Test_loggerpackage_log_message:
    """ibr_logger_packageのLoggerPackageクラス _create_message_tableメソッドのテスト全体をまとめたClass

    このテストはlogger機能自体のテストであることから
    標準出力にはprint文を使用することを許容する
    print文でのassertが必要な場合はcapdf fixtureを使用すること

    LoggerPackage実行により生成された各種self.xxxxxを使用して カスタムロガーを生成する。
    カスタムロガーの各種機能を検証する

    C0: 命令カバレッジ
        - 正常実行,カスタムロガー生成
        - 例外
            - Exception
    C1: 分岐カバレッジ
    C2: 条件カバレッジ
    """
    def test_loggerpackage_log_message_UT_C0_normal(
        self,
        mocker:MagicMock,
        caplog: pytest.LogCaptureFixture,
        capfd: pytest.LogCaptureFixture,
        _reset_singleton_instance,
        create_config:(Path, Path),
        ) -> None:
        # テスト定義ログ出力はこのまま書いてください、改修不要
        test_doc = """
        - テスト定義:
                - テストカテゴリ: C0
                - テスト区分: 正常系/UT
                - テストシナリオ: カスタムロガーによるMSG出力
                    - LogLevel 制御の妥当性チェック
                    - msg_tableにヒットしないKeyを指定
        """
        test_functions = [func for func in dir(self) if callable(getattr(self, func)) and func.startswith('test')]
        func_info = f"        - テスト関数: {', '.join(test_functions)}"
        print(f"\n{func_info}{test_doc}", LogLevel.DEBUG)

        # toml取得
        # strのまま実行
        test_config_toml, test_package_toml = create_config

        # sysout capture test - default
        package_path = Path(__file__)
        logger_package = LoggerPackage(package_path)
        log_msg = logger_package.log_message

        # sysout capture test - DEBUG
        expected_1 = '[DEBUG] common_utils.test_ibr_logger_package::test_loggerpackage_log_messag'
        expected_2 = 'test_1'
        log_msg('test_1', LogLevel.DEBUG)
        captured = capfd.readouterr()
        # DEBUGなのでsdoutでキャプチャーされない
        assert not expected_1 in captured.out
        assert not expected_2 in captured.out

        # logger.name 確認
        expected_1 = '[INFO] common_utils.test_ibr_logger_package::test_loggerpackage_log_message'
        expected_2 = 'test_1'
        log_msg('test_1')
        captured = capfd.readouterr()
        assert expected_1 in captured.out
        assert expected_2 in captured.out

        # sysout capture test - WARNING
        expected_1 = '[WARNING] common_utils.test_ibr_logger_package::test_loggerpackage_log_message'
        expected_2 = 'test_1'
        log_msg('test_1', LogLevel.WARNING)
        captured = capfd.readouterr()
        assert expected_1 in captured.out
        assert expected_2 in captured.out

        # sysout capture test - ERROR
        expected_1 = '[ERROR] common_utils.test_ibr_logger_package::test_loggerpackage_log_message'
        expected_2 = 'test_1'
        log_msg('test_1', LogLevel.ERROR)
        captured = capfd.readouterr()
        assert expected_1 in captured.out
        assert expected_2 in captured.out

        # sysout capture test - CRITICAL
        expected_1 = '[CRITICAL] common_utils.test_ibr_logger_package::test_loggerpackage_log_message'
        expected_2 = 'test_1'
        log_msg('test_1', LogLevel.CRITICAL)
        captured = capfd.readouterr()
        assert expected_1 in captured.out
        assert expected_2 in captured.out

        # sysout capture test - XXXXXXXXXXX
        expected_1 = '[INFO] common_utils.test_ibr_logger_package::test_loggerpackage_log_message'
        expected_2 = 'test_1'
        log_msg('test_1', 999999999999)
        captured = capfd.readouterr()
        assert expected_1 in captured.out
        assert expected_2 in captured.out


    def test_loggerpackage_log_message_UT_C0_normal_specfy_message_key(
        self,
        mocker:MagicMock,
        caplog: pytest.LogCaptureFixture,
        capfd: pytest.LogCaptureFixture,
        _reset_singleton_instance,
        create_config:(Path, Path),
        ) -> None:
        # テスト定義ログ出力はこのまま書いてください、改修不要
        test_doc = """
        - テスト定義:
                - テストカテゴリ: C0
                - テスト区分: 正常系/UT
                - テストシナリオ: カスタムロガーによるMSG出力
                    - msg_tableにヒットするKeyを指定
        """
        test_functions = [func for func in dir(self) if callable(getattr(self, func)) and func.startswith('test')]
        func_info = f"        - テスト関数: {', '.join(test_functions)}"
        print(f"\n{func_info}{test_doc}", LogLevel.DEBUG)

        # toml取得
        # strのまま実行
        test_config_toml, test_package_toml = create_config

        # sysout capture test - default
        package_path = 'test_package'
        logger_package = LoggerPackage(package_path)
        log_msg = logger_package.log_message

        # sysout capture test - DEBUG
        # sysoutには出力されない
        expected_1 = '[INFO] common_utils.test_ibr_logger_package::test_loggerpackage_log_message'
        expected_2 = '起動しました'
        log_msg("IBRDEV-I-0000001", LogLevel.DEBUG)
        captured = capfd.readouterr()
        assert not expected_1 in captured.out
        assert not expected_2 in captured.out


    def test_loggerpackage_log_message_UT_C0_raise_exception(
        self,
        mocker: MagicMock,
        capfd: pytest.LogCaptureFixture,
        caplog: pytest.LogCaptureFixture,
        _reset_singleton_instance,
        ) -> None:
        # テスト定義ログ出力はこのまま書いてください、改修不要
        test_doc = """
        - テスト定義:
                - テストカテゴリ: C0
                - テスト区分: 正常系/UT
                - テストシナリオ: Config生成、格納Object確認
        """
        test_functions = [func for func in dir(self) if callable(getattr(self, func)) and func.startswith('test')]
        func_info = f"        - テスト関数: {', '.join(test_functions)}"
        print(f"\n{func_info}{test_doc}", LogLevel.DEBUG)

        # caplogを使ってログメッセージをキャプチャ
        caplog.set_level(LogLevel.ERROR.value)

        # 期待されるログメッセージ
        expected_sysout_msg = "カスタムロガーメッセージ出力に失敗しました"

        package_path = Path(__file__)
        logger_package = LoggerPackage(package_path)
        mocker.patch.object(logger_package, 'log_message', side_effect=Exception)
        with pytest.raises(Exception):
            logger_package.log_message("IBRDEV-I-0000001", LogLevel.ERROR)
            captured = capfd.readouterr()

            # ログメッセージが期待通りのものか確認
            assert expected_sysout_msg in captured.out


