"""csvファイル処理のヘルパーライブラリ"""

import csv
import os
import traceback
from pathlib import Path

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
def import_csv_to_row(file_path: str|Path, delimiter: str=',') -> list[list[str]]:
    """csvファイルをlistに格納する

    - 指定したcsvファイルを読み取り、listへ格納する
    - delimiterの指定が可能

    Copy right:
        (あとで書く)

    Args:
        file_path (str | Path): _description_
        delimiter (str): defalut=',' _description_

    Returns:
        (list[list[str]]): csvファイルを格納した2次元文字列リスト

    Raises:
        - FileNotFound
        - PermissionError
        - IsADirectoryError
        - MemoryError
        - Exception

    Example:
        >>> _list = import_csv_to_row('./test.csv')
        >>> _list = import_csv_to_row(Path('./test.csv'))

    Notes:
        ...

    Changelog:
        - v1.0.0 (2024/01/01): Initial release
        -
    """
    file_path = Path(file_path)

    try:
        with file_path.open(mode='r', encoding='utf8', newline='') as f:
            return list(csv.reader(f, delimiter=delimiter))
    except FileNotFoundError as e:
        log_msg(f'can not get target files {e}', LogLevel.ERROR)
        raise
    except PermissionError as e:
        log_msg(f'No permission to read the file: {e}', LogLevel.ERROR)
        raise
    except IsADirectoryError as e:
        log_msg(f'The specified path is a directory, not a file: {e}', LogLevel.ERROR)
        raise
    except MemoryError as e:
        log_msg(f'Not enough memory to read csv file: {e}', LogLevel.ERROR)
        raise
    except Exception as e:
        tb = traceback.TracebackException.from_exception(e)
        log_msg(''.join(tb.format()), LogLevel.ERROR)
        raise


def import_csv_to_dataframe(
    file_path: str|Path,
    sep: str=',',
    header: int=0,
    skiprows: int=0,
    encoding: str='utf-8',
    dtype: str|dict='object',
    engine: str='python',
    usecols: list|None=None,
    ) -> pd.DataFrame|None:
    """csvファイルを読み込みDataFrameへ格納する

    - 指定したcsvファイルを読み取り、DataFrameへ格納する
    - delimiterの指定が可能
    - デフォルトではデータ全列を取り込む、列指定する場合はusecolsで指定する
    - その他状況時応じてパラメータを指定する

    Copy right:
        (あとで書く)

    Args:
        file_path (str | Path): csvファイルパス
        sep (str): default=',' データセパレータ
        header (int): default=0 ヘダー行判定、デフォルトでは先頭行がタイトル
        skiprows (int): default=0 Excelシート上で読み飛ばす行数、データ始まり位置指定
        encoding (str): default='utf-8 ' 文字コード
        dtype (str | dict): default='object' DataFrameに取り込む列型を一律指定
        engine (str): default='python' 変換エンジン指定
        usecols (list | None): default=None 取り込む列指定、デフォルトでは全列取り込み

    Returns:
        (pd.DataFrame|None): csvファイルを取り込んだDataFrame

    Raises:
        - FileNotFoundError
        - PermissionError
        - IsADirectoryError
        - pd.errors.ParserError
        - MemoryError
        - Exception

    Example:
        >>> (sample code)

    Notes:
        _description_

    Changelog:
        - v1.0.0 (2024/01/01): Initial release
        -
    """
    na_values = ['-', 'Nan', 'null']

    file_path = Path(file_path)

    try:
        _df = pd.read_csv(
            file_path,
            sep=sep,
            header=header,
            skiprows=skiprows,
            na_values=na_values,
            encoding=encoding,
            dtype=dtype,
            engine=engine,
            usecols=usecols,
        )
    except FileNotFoundError as e:
        log_msg(f'can not get target files {e}', LogLevel.ERROR)
        raise
    except PermissionError as e:
        log_msg(f'No permission to read the file: {e}', LogLevel.ERROR)
        raise
    except IsADirectoryError as e:
        log_msg(f'The specified path is a directory, not a file: {e}', LogLevel.ERROR)
        raise
    except pd.errors.ParserError as e:
        log_msg(f'Failed to parse the Excel file: {e}', LogLevel.ERROR)
        raise
    except pd.errors.EmptyDataError as e:
        log_msg(f'Failed to parse the empty Excel file : {e}', LogLevel.ERROR)
        raise
    except MemoryError as e:
        log_msg(f'Not enough memory to read csv file: {e}', LogLevel.ERROR)
        raise
    except Exception as e:
        tb = traceback.TracebackException.from_exception(e)
        log_msg(''.join(tb.format()), LogLevel.ERROR)
        raise
    else:
        return _df
    finally:
        pass


def get_file_record_count(file_path: str|Path, header: int=0) -> int|None: # noqa: PLR0911 ファイルI/O制御のため許容
    r"""データレコード件数(ヘダー込み)を取得する

    - ヘダー込みでデータ件数を返す
    - headerパラメータによりヘダー行を減算が可能

    Copy right:
        (あとで書く)

    Args:
        file_path (str | Path): レコード件数カウント対象ファイルパス
        header (int): default=0 ヘダー行をカウント除外する際に指定する,指定数分を減算する

    Returns:
        (int|None): データレコード数

    Raises:
        - FileNotFoundError
        - PermissionError
        - IsADirectoryError
        - MemoryError
        - Exception

    Example:
        >>> record_count = get_file_record_count('./data.txt')

    Notes:
        テキストに限らずバイナリファイルでも行数認識できるなら件数取得可能です

    Changelog:
        - v1.0.0 (2024-01-01): Initial release
        -
    """
    file_path = Path(file_path)
    header = int(header)

    if header < 0:
        log_msg(f'header values must >= 0: {header} ', LogLevel.ERROR)
        return None
    try:
        with file_path.open(mode='rb') as f:
            record_count = sum(1 for line in f)
    except FileNotFoundError as e:
        log_msg(f'can not get target files {e}', LogLevel.ERROR)
        return None
    except PermissionError as e:
        log_msg(f'No permission to read the file: {e}', LogLevel.ERROR)
        return None
    except IsADirectoryError as e:
        log_msg(f'The specified path is a directory, not a file: {e}', LogLevel.ERROR)
        return None
    except MemoryError as e:
        log_msg(f'Not enough memory to read csv file: {e}', LogLevel.ERROR)
        return None
    except Exception as e: # noqa: BLE001 exception最終句に設定
        tb = traceback.TracebackException.from_exception(e)
        log_msg(''.join(tb.format()), LogLevel.ERROR)
        return None
    else:
        return record_count - header


def _write_records(cnt_file_path: int|Path, records: list[str]) -> None:
    """CNTファイル作成ヘルパー関数"""
    cnt_file_path = Path(cnt_file_path)
    try:
        with cnt_file_path.open(mode='w', encoding='utf-8') as f:
            for record in records:
                f.write(f'{record}\n')
    except Exception as e:
        tb = traceback.TracebackException.from_exception(e)
        log_msg(''.join(tb.format()), LogLevel.ERROR)
        raise


def create_cnt_file(csv_file_path: str|Path, cnt_file_path: str|Path, csv_header_record: int=1) -> bool:
    """ファイル転送仕様に基づき制御ファイルを作成する

    - ファイル転送仕様に基づきCNTファイルを作成する
    - デフォルト想定では転送対象ファイルはヘダー行が1行の構成
    - 制御ファイルに出力するパラメータは以下の通り
        'SIZE=対となるデータファイル件数'
        'CLASS=0'
        'STAT=0'
        'EOF'

    Copy right:
        (あとで書く)

    Args:
        csv_file_path (str | Path): 制御ファイルと対になるデータへのフルパス
        cnt_file_path (str | Path): 制御ファイル出力フルパス
        csv_header_record (int): default=1, ヘダーファイルがある前提、調整可能

    Returns:
        (bool): True: 制御ファイル作成に成功, False: 制御ファイル作成失敗

    Raises:
        ...

    Example:
        >>> if create_cnt_file('./test.txt', 'test.cnt'):
        >>>     log_msg('制御ファイル作成に成功しました', LogLevel.INFO)

    Notes:
        以下の関数に依存しています
        - get_file_record_count()
        - _write_records()

    Changelog:
        - v1.0.0 (2024/01/01): Initial release
        -
    """
    csv_file_path = Path(csv_file_path)
    cnt_file_path = Path(cnt_file_path)

    # 書き込み権限は事前チェック
    if not cnt_file_path.parent.exists() or \
        not os.access(cnt_file_path.parent, os.W_OK):
        log_msg(f'CNTファイル作成のディレクトリに書き込み権限がありません: {cnt_file_path}', LogLevel.ERROR)
        return False

    if csv_header_record < 0:
        log_msg(f'header values must >= 0: {csv_header_record} ', LogLevel.ERROR)
        return False

    # 評価対象ファイルのデータ件数取得
    record_count = get_file_record_count(csv_file_path, csv_header_record)
    if (record_count is None) or (record_count < 0):
        log_msg(f'対象ファイルの件数取得に失敗しました: {csv_file_path}', LogLevel.ERROR)
        return False
    log_msg(f"対象ファイルレコード数(除くヘダー行): {record_count}", LogLevel.INFO)

    # CNTファイル作成
    records = [
        f'SIZE={record_count}',
        'CLASS=0',
        'STAT=0',
        'EOF',
    ]
    try:
        _write_records(cnt_file_path, records)
    except Exception as e: # noqa: BLE001 exception最終句に設定
        log_msg(f'CNTファイル出力に失敗しました: {e}', LogLevel.ERROR)
        log_msg(f'cnf_file_path: {cnt_file_path}', LogLevel.ERROR)
        tb = traceback.TracebackException.from_exception(e)
        log_msg(''.join(tb.format()), LogLevel.ERROR)
        return False
    else:
        log_msg(f'cntファイル作成: {cnt_file_path}', LogLevel.INFO)
        return True
