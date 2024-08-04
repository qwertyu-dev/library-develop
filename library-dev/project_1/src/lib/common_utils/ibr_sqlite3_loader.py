"""sqlite3サポートライブラリ"""
import sqlite3
import traceback

import pandas as pd
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
class Sqlite3Manager:
    """sqlite3操作サポートライブラリ"""
    def __init__(self, db_path: str):
        # sqlite3 DBファイルパス設定
        self.db_path = db_path

    def load_dataframe_to_sqlite3(self, df: pd.DataFrame, tablename: str, if_exists: str='replace') -> bool:
        """DataFrameをsqlite3へロードする

        - デフォルトではreplaceの挙動を行う
        - パラメータ設定によりappendなどの挙動に切替が可能

        Copy right:
            (あとで書く)

        Args:
            df (pd.DataFrame): データ保有するDataFrame
            tablename (str): sqlite3 DBファイルパス
            if_exists (str): default='replace' データロード挙動定義

        Returns:
            (bool): True 成功, False 失敗

        Raises:
            - sqlite3Error
            - Exception

        Example:
            >>> _load_sqlite3 = Sqlite3Manager('./db.sqlte3')
            >>> _load_sqlite3.load_data_to_sqlite(_df, tablename='test.table')


        Notes:
            データ管理方式に応じて挙動定義を行う
            挙動それぞれに応じてテーブルリカバリー手順を定義すること

        Changelog:
            - v1.0.0 (2024/01/01): Initial release
            -
        """
        if not isinstance(df, pd.DataFrame):
            log_msg('DBロードファイルにDataFrameを指定していません')
            return False

        try:
            with sqlite3.connect(self.db_path) as conn:
                df.to_sql(tablename, conn, if_exists=if_exists)
        except sqlite3.Error as e:
            log_msg(f'sqlite3エラー: {e}', LogLevel.ERROR)
            return False
        except Exception as e: # noqa: BLE001 sqlite3の例外は前ステップでハンドリングしている、許容
            tb = traceback.TracebackException.from_exception(e)
            log_msg(''.join(tb.format()), LogLevel.ERROR)
            return False
        else:
            return True


    def execute_sql_sqlite3(self, sqltext: str) -> bool:
        """指定SQLを実行する

        Copy right:
            (あとで書く)

        Args:
            sqltext (str): 実行するSQL文

        Returns:
            (bool): True 成功, False 失敗

        Raises:
            - sqlite3Error
            - Exception

        Example:
            >>> _load_sqlite3 = Sqlite3Manager('./db.sqlite3')
            >>> _load_sqlite3.execute_sql_sqlite3('UPDATE test_table SET ----')

        Notes:
            保守用のSQL実行を想定しています

        Changelog:
            - v1.0.0 (2024/01/01): Initial release
            -
        """
        if not isinstance(sqltext, str):
            log_msg(f'sql must be a string: {sqltext}', LogLevel.ERROR)
            return False

        if not sqltext:
            log_msg(f'SQL text is empty: {sqltext}', LogLevel.ERROR)
            return False

        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute(sqltext)
                conn.commit()
        except sqlite3.Error as e:
            log_msg(f'sqlite3エラー: {e}', LogLevel.ERROR)
            return False
        except Exception as e: # noqa: BLE001 sqlite3の例外は前ステップでハンドリングしている、許容
            tb = traceback.TracebackException.from_exception(e)
            log_msg(''.join(tb.format()), LogLevel.ERROR)
            return False
        else:
            return True


    def fetch_sql_sqlite3(self, sqltext:str) -> list[list[str]]|None:
        """sqlite3テーブルからfetchでデータ取り出し

        sqltextに記述したSQLによりデータを取り出しlistに格納する

        Copy right:
            (あとで書く)

        Args:
            sqltext (str): データ抽出SQL

        Returns:
            (list[list[str]]|None): SQLで取り出したデータをlistへ格納する

        Raises:
            - sqlite3Error
            - Exception

        Example:
            >>> _load_sqlite3 = Sqlite3Manager('./db.sqlite3')
            >>> _list = _load_sqlite3.fetch_sql_sqlite3('SELECT * FROM test_table')

        Notes:
            データ取得処理を前提にしています

        Changelog:
            - v1.0.0 (2024/01/01): Initial release
            -
        """
        if not isinstance(sqltext, str):
            log_msg(f'sql must be a string: {sqltext}', LogLevel.ERROR)
            return None

        if not sqltext:
            log_msg(f'SQL text is empty: {sqltext}', LogLevel.ERROR)
            return None

        try:
            with sqlite3.connect(self.db_path) as conn:
                cur = conn.cursor()
                cur.execute(sqltext)
                return cur.fetchall()
        except sqlite3.Error as e:
            log_msg(f'sqlite3エラー: {e}', LogLevel.ERROR)
            return None
        except Exception as e: # noqa: BLE001 sqlite3の例外は前ステップでハンドリングしている、許容
            tb = traceback.TracebackException.from_exception(e)
            log_msg(''.join(tb.format()), LogLevel.ERROR)
            return None

