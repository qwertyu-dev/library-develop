"""カスタムロガーサポートライブラリ"""
import inspect
import os
import socket
import sys
import traceback
from json import load
from logging import (
    INFO,
    Logger,
    config,
    getLogger,
)
from pathlib import Path
from typing import (
    Any,
    ClassVar,
)

import toml
from src.lib.common_utils.ibr_enums import (
    ExecEnvironment,
    LogLevel,
)


##################################
# class 定義
##################################
class SingletonType(type):
    """Singleton構成を定義する

    いわゆるSingletonそのものになります

    Notes:
        テストコードを実行する際はOSの環境変数設定が必要になります
        $Env:EXEC_PATTERN = 'tests'  or export EXEC_PATTERN=tests

    Copy right:
        (あとで書く)

    Changelog:
        - v1.0.0 (2024/01/01): Initial release
        -
    """
    _instances: ClassVar[dict[type, Any]] = {}

    def __call__(cls, *args: str, **kwargs: str):
        """Singleton呼び出し定義

        Class変数でinstance生成管理を行いすでにインスタンス起動されていたら
        新規でインスタンス生成は制御を行う。

        バッチ処理システムを前提としているため
        パッケージ起動毎に多重起動しない制御を行う

        Args:
            None
                当初引数を想定していたが仕様変更で引数なし
                testコード実装のためだけに仕様が複雑になるのを避けるため、tests実施の際はOS環境設定変数から
                判定材料を得ることにした
                またSingletonを使用しているため、仕様を複雑にしないように考慮した結果

        Copy right:
            (あとで書く)

        Notes:
            異なるパッケージの多重起動までは想定していない。
            その役割はJP1などのでのジョブ制御が担当する。

        Changelog:
            - v1.0.0 (2024/01/01): Initial release
            -
        """
        if cls not in cls._instances:
            #cls._instances[cls] = super().__call__(*args, **kwargs)
            cls._instances[cls] = super().__call__()

        return cls._instances[cls]

    @classmethod
    def reset_instances(cls) -> None:
        cls._instances.clear()



class LoggerPackage(metaclass=SingletonType):
    """カスタムロガー定義

    以下の機能を追加したカスタムロガー提供定義
        - Singleton制御
        - MSG定義検索、ログ出力機能付加

    Copy right:
        (あとで書く)

    Args:
        metaclass (_type_): default=SingletonType Singletonインスタンス制御縛り定義


    Changelog:
        - v1.0.0 (2024/01/01): Initial release
        -
    """

    def __init__(self):
        # ロガー識別設定
        self._name = Path(__file__).name

        # src/tests を環境変数(EXEC_PATTERN)
        self._exec_pattern = os.environ.get('EXEC_PATTERN', 'src')

        # log_msg()向けconfig情報取得
        try:
            self._get_exec_env()
            self._get_config_dict()
            self._create_logger()
            self._create_msg_table()
        except Exception as e:
            print(f'Config生成に失敗しました: {e}',LogLevel.ERROR)
            tb = traceback.TracebackException.from_exception(e)
            print(''.join(tb.format()), LogLevel.ERROR)
            raise SystemExit from e

    def _get_enum_value(self, enum: enumerate, key: str, default: str) -> str:
        """EnumをKey検索するヘルパー"""
        try:
            enum_value = enum.__members__.get(key, default).value
        except Exception as e:
            print(f'Enumからの値取得に失敗しました: {e}') # noqa: T201
            raise
        else:
            return enum_value

    def _get_exec_env(self) -> None:
        # 実行ホスト名取得
        # 実行ホスト名→環境判別ラベル取得
        try:
            _hostname = socket.gethostname()
            self._env = self._get_enum_value(ExecEnvironment, _hostname, ExecEnvironment.HOSTNAME_LOCAL)
        except Exception as e:
            print(f'ホスト名の取得に失敗しました: {e}') # noqa: T201
            raise

    def _toml_parser(self, toml_path: str|Path) -> dict:
        """tomlから値(dict格納)取得ヘルパー"""
        toml_path = Path(toml_path)
        try:
            with toml_path.open(mode='r', encoding='utf-8') as f:
                toml_obj = toml.load(f)
        except FileNotFoundError as e:
            print(f'can not get target files: {e}', LogLevel.ERROR) # noqa: T201
            raise
        except PermissionError as e:
            print(f'No permission to read the file: {e}', LogLevel.ERROR) # noqa: T201
            raise
        except IsADirectoryError as e:
            print(f'The specified path is a directory, not a file: {e}')  # noqa: T201
            raise
        except Exception as e:
            tb = traceback.TracebackException.from_exception(e)
            print(''.join(tb.format()), LogLevel.ERROR) # noqa: T201
            raise
        else:
            return toml_obj

    def _get_config_dict(self) -> None:
        common_toml_path = Path(f'{self._exec_pattern}/def/common_config/common_config.toml')
        # logger定義,MSG定義を取得
        try:
            self._common_config = self._toml_parser(common_toml_path)
        except Exception as e:
            print(f'logger定義の取得に失敗しました: {e}') # noqa: T201
            raise

    def _create_logger(self) -> None:
        self.LOGGER_DEF_FILE = Path(f"{self._common_config[self._env]['logger_path']['LOGGER_DEF_FILE']}")
        # 取得したlogger定義からlogger生成
        try:
            with self.LOGGER_DEF_FILE.open(mode='r', encoding='utf-8') as f:
                config.dictConfig(load(f))
                self._logger = getLogger(self._name)
        except Exception as e:
            print(f'logger定義の生成に失敗しました: {e}') # noqa: T201
            raise

    def _create_msg_table(self) -> None:
        # 取得したmsgテーブル定義からmsgテーブルを生成
        # common_configにMSGテーブル定義Pathの記述がある
        self.LOGGER_MSG_FILE = Path(f"{self._common_config[self._env]['logger_path']['LOGGER_MSG_FILE']}")
        try:
            toml_load = self._toml_parser(self.LOGGER_MSG_FILE)
            self._message_table = toml_load['DEF_IBRDEV_MSGS']
        except Exception as e:
            print(f'msg_table定義の生成に失敗しました: {e}') # noqa: T201
            raise


    def log_message(self, msg_id: str, level:LogLevel=LogLevel.INFO) -> None:
        """機能追加版カスタムロガー実体

        - MSGテーブルに対しmsg_idで検索、ヒットすれば対となるMSGをロガーに出力する
        - MSGテーブルにないmsg_idの場合はそのmsg_idをロガーに出力する(テーブルに定義なければそのままロガー出力)
        - loggerのログレベルに準拠してロガー出力する
        - loggerでの実行パッケージは呼び出し側、呼び出され側で実体パッケージをラベル出力する

        Copy right:
            (あとで書く)

        Args:
            msg_id (str): MSGテーブル検索Key
            level (str): loggerのログレベル

        Returns:
            ...

        Raises:
            ...

        Example:
            >>> from src.lib.common_utils.ibr_get_config import Config
            >>> package_path = Path(__file__)
            >>> logger_package = LoggerPackage(package_path)
            >>> log_msg = logger_package.log_message
            >>> log_msg('aaaaa', LogLevel.INFO)

        Notes:
            logger定義及びMSG定義テーブルに依存します

        Changelog:
            - v1.0.0 (2024/01/01): Initial release
            -
        """
        # 呼び出し元logger情報退避
        old_logger_name = self._logger.name

        # msg定義テーブル検索
        message = self._message_table.get(msg_id, '')

        # フレーム情報取得
        caller_frame = inspect.currentframe().f_back

        # ファイルパスからパッケージ名を推察
        file_path = Path(caller_frame.f_globals['__file__'])
        package_name = file_path.parent.name

        # 関数名を取得、行数取得
        func_name = caller_frame.f_code.co_name
        caller_lineno = caller_frame.f_lineno

        # logger.name差し替え
        self._logger.name = package_name

        # 書き出し、ログレベルに応じて出力
        try:
            if level == LogLevel.DEBUG:
                self._logger.debug(f'{func_name} line {caller_lineno}: {msg_id}:{str(message)}')
            elif level == LogLevel.INFO:
                self._logger.info(f'{func_name} line {caller_lineno}: {msg_id}:{str(message)}')
            elif level == LogLevel.WARNING:
                self._logger.warning(f'{func_name} line {caller_lineno}: {msg_id}:{str(message)}')
            elif level == LogLevel.ERROR:
                self._logger.error(f'{func_name} line {caller_lineno}: {msg_id}:{str(message)}')
            elif level == LogLevel.CRITICAL:
                self._logger.critical(f'{func_name} line {caller_lineno}: {msg_id}:{str(message)}')
            else:
                self._logger.info(f'{func_name} line {caller_lineno}: {msg_id}:{str(message)}')
        except Exception as e:
            print(f'カスタムロガーメッセージ出力に失敗しました: {e}') # noqa: T201
            raise
            ...
        # loggerをもとに戻す
        finally:
            self._logger.name = old_logger_name

