"""危険なファイル操作サポートライブラリ"""
from datetime import datetime
import os
import shutil
import traceback
from pathlib import Path
from dateutil import tz
from src.lib.common_utils.ibr_enums import LogLevel
from src.lib.common_utils.ibr_logger_package import LoggerPackage

################################
# logger
################################
logger = LoggerPackage(__package__)
log_msg = logger.log_message

################################
# tz生成
################################
JST = tz.gettz('Aaia/Tokyo')

################################
# function
################################
def _precheck_read_file(file_path: str | Path) -> bool:
    """ファイル読み込み権限チェックヘルパー"""
    file_path = Path(file_path)

    if not file_path.exists() or not file_path.is_file():
        log_msg(f'指定ファイルが存在しません - {file_path}', LogLevel.ERROR)
        return False
    if not os.access(file_path, os.R_OK):
        log_msg(f'指定ファイルに読み取り権限がありません - {file_path}', LogLevel.ERROR)
        return False
    return True


def _precheck_write_file(destination_directory: str|Path) -> bool:
    """ファイル書き込み権限チェックヘルパー"""
    destination_directory = Path(destination_directory)

    if not destination_directory.exists() or not destination_directory.is_dir():
        log_msg(f'指定ディレクトリが存在しません: {destination_directory}', LogLevel.ERROR)
        return False
    if not os.access(destination_directory, os.W_OK):
        log_msg(f'指定ディレクトリに書き込み権限がありません: {destination_directory}', LogLevel.ERROR)
        return False
    return True


def delete_file(file_path: str|Path) -> bool:
    """ファイル削除操作

    ファイル削除操作には危険が伴う
    プレチェックを行うことでリスク軽減を行う

    Copy right:
        (あとで書く)

    Args:
        file_path (str | Path): 削除対象ファイルパス

    Returns:
        (bool): True ファイル削除成功, False ファイル削除失敗

    Raises:
        - FileNotFoundError
        - PermissionError
        - IsADirectoryError

    Example:
        >>> delete_file('./test.txt')

    Notes:
        _precheck_read_file()

    Changelog:
        - v1.0.0 (2024/01/01): Initial release
        -
    """
    #  ファイル削除可否チェック
    if not _precheck_read_file(file_path):
        return False

    # ファイル削除
    try:
        file_path.unlink()
    except Exception as e:
        tb = traceback.TracebackException.from_exception(e)
        log_msg(''.join(tb.format()), LogLevel.ERROR)
        raise
    else:
        return True


def move_file(old_file_path: str|Path, destination_directory: str|Path, overwrite: bool=False, with_timestamp: bool=True) -> bool | Path|None:
    """ファイル移動操作

    ファイル移動操作には危険が伴う
    プレチェックを行うことでリスク軽減を行う

    - 同一ファイル名で別ディレクトリへのファイル移動を行う
    - 移動先に同一ファイル名がすでに存在している場合、上書き可否の判定で対応する
    - pathlib.Path.replace()を使用することで上書き許容を機能にもたせる

    Copy right:
        (あとで書く)

    Args:
        old_file_path (str | Path): 移動元ファイルパス
        destination_directory (str | Path): 移動先ディレクトリパス
        overwrite (int): default=0 上書き可否判定(デフォルトNG), 上書き可とする場合は0以外の数字を設定する
        with_timestamp (int): default=1 0以外でタイムスタンプ付与してファイル移動、0の場合はタイムスタンプ付与なし

    Returns:
        (bool): True 成功, False 失敗
        (Path): 移動ファイルPath

    Raises:
        - Exception ファイル移動中の異常発生

    Example:
        >>> move_file('./test.txt", '/temp') 上書き不可で/tmpへ移動, タイムスタンプ付与あり
        >>> move_file('./test.txt", '/temp', overwrite=1) 上書き可で/tmpへ移動, タイムスタンプ付与あり
        >>> move_file('./test.txt", '/temp', overwrite=0, with_timestamp=0) 上書き不可で/tmpへ移動,タイムスタンプ付与なし

    Notes:
        _description_

    Changelog:
        - v1.0.0 (2024/01/01): Initial release
        -
    """
    old_file_path = Path(old_file_path)
    old_file_name = old_file_path.name
    destination_directory = Path(destination_directory)

    # timestamp付与有無生成
    if with_timestamp:
        timestamp = datetime.now(tz=JST).strftime("%Y%m%d_%H%M%S")
        file_name, file_extension = old_file_name.rsplit('.', 1)
        new_file_name = f"{file_name}_{timestamp}.{file_extension}"
    else:
        new_file_name = old_file_name

    new_file_path = destination_directory / new_file_name

    # 変更元ファイルに読み込み権限があるか
    if not _precheck_read_file(old_file_path):
        return (False, None)

    # 変更先ファイル配置ディレクトリに書き込み権限があるか
    if not _precheck_write_file(destination_directory):
        return (False, None)

    # 存在ファイルへの上書きNG設定の場合、デフォルトで上書きNG
    if not overwrite and new_file_path.exists():
            log_msg(f'同じ名前のファイルが存在しています: {new_file_path}', LogLevel.ERROR)
            return (False, None)

    # ファイル移動
    try:
        old_file_path.replace(new_file_path)
        log_msg(f'ファイル{old_file_path}を{new_file_path}に移動しました')
    except Exception as e:
        tb = traceback.TracebackException.from_exception(e)
        log_msg(''.join(tb.format()), LogLevel.ERROR)
        raise
    else:
        return (True, new_file_path)


def rename_file(old_file_path: str|Path, new_file_name: str, overwrite:int=0) -> bool|  Path|None:
    """ファイルリネーム操作

    ファイルリネーム操作には危険が伴う
    プレチェックを行うことでリスク軽減を行う

    同一ディレクトリ上で対象ファイルを指定ファイル名でリネームする

    Copy right:
        (あとで書く)

    Args:
        old_file_path (str | Path): リネーム元ファイルパス
        new_file_name (str): リネーム後ファイル名
        overwrite (int): default=0 上書き可否判定(デフォルトNG), 上書き可とする場合は0以外の数字を設定する

    Returns:
        (bool): True 成功, False 失敗
        (Path): リネームしたファイルPath

    Raises:
        - Exception ファイル移動中の異常発生

    Example:
        >>> rename_file('./test.txt/, 'rename.txt')
        >>> rename_file('./test.txt/, 'rename.txt', overwrite=1)

    Notes:
        ...

    Changelog:
        - v1.0.0 (2024/01/01): Initial release
        -
    """
    old_file_path = Path(old_file_path)
    old_file_directory = old_file_path.parent
    new_file_path = old_file_directory / new_file_name

    # 変更元ファイルに読み込み権限があるか
    if not _precheck_read_file(old_file_path):
        return (False, None)

    # リネーム操作ディレクトリに書き込み権限があるか
    if not _precheck_write_file(old_file_directory):
        return (False, None)

    # 存在ファイルへの上書きNG設定の場合、デフォルトで上書きNG
    if not overwrite and new_file_path.exists():
            log_msg(f'同じ名前のファイルが存在しています: {new_file_path}', LogLevel.ERROR)
            return (False, None)

    # ファイル名変更
    try:
        old_file_path.rename(new_file_path)
        log_msg(f'ファイル{old_file_path}の名前を{new_file_path}に変更しました')
    except Exception as e:
        tb = traceback.TracebackException.from_exception(e)
        log_msg(''.join(tb.format()), LogLevel.ERROR)
        raise
    else:
        return (True, new_file_path)


def copy_file(source_file_path: str|Path, destination_directory: str|Path, overwrite: bool=False, with_timestamp: bool=False) -> bool |  Path|None:
    """ファイルコピー操作

    ファイルコピー操作には危険が伴う
    プレチェックを行うことでリスク軽減を行う

    同一ファイル名で別ディレクトリへファイルコピーします
    日付因子を付与してコピー指定が可能です

    Copy right:
        (あとで書く)

    Args:
        source_file_path (str | Path): ファイルコピー元パス
        destination_directory (str | Path): コピー先ディレクトリパス
        overwrite (int): default=0 上書き可否判定(デフォルトNG), 上書き可とする場合は0以外の数字を設定する
        with_timestamp(int): default=0 コピーファイルにタイムスタンプ付与しない,付与する場合は0以外の数字を設定する

    Returns:
        (bool): True 成功, False 失敗
        (Path): コピー先ファイルPath

    Raises:
        - Exception ファイル移動中の異常発生

    Example:
        >>> file_copy('./text.txt', '/tmp')
        >>> file_copy('./text.txt', '/tmp', overwrite=1)
        >>> file_copy('./text.txt', '/tmp', with_timestamp=1)

    Notes:
        ...

    Changelog:
        - v1.0.0 (2024/01/01): Initial release
        -
    """
    # 資源生成
    source_file_path = Path(source_file_path)
    source_file_name = source_file_path.name
    destination_directory = Path(destination_directory)

    # ファイルにタイムスタンプ付与するかの判定処理
    if  with_timestamp:
        timestamp = datetime.now(tz=JST).strftime("%Y%m%d_%H%M%S")
        file_name, file_extension = source_file_name.rsplit('.', 1)
        new_file_name = f"{file_name}_{timestamp}.{file_extension}"
        new_file_path = destination_directory / new_file_name
    else:
        new_file_path = destination_directory / source_file_name

    # 変更元ファイルに読み込み権限があるか
    if not _precheck_read_file(source_file_path):
        return (False, None)

    # 変更先ファイル配置ディレクトリに書き込み権限があるか
    if not _precheck_write_file(destination_directory):
        return (False, None)

    # 存在ファイルへの上書きNG設定の場合、デフォルトで上書きNG
    if not overwrite and new_file_path.exists():
        log_msg(f'同じ名前のファイルが存在しています: {new_file_path}', LogLevel.ERROR)
        return False

    try:
        shutil.copy2(source_file_path, new_file_path)
        log_msg(f'ファイル{source_file_path}を{new_file_path}にコピーしました')
    except Exception as e:
        tb = traceback.TracebackException.from_exception(e)
        log_msg(''.join(tb.format()), LogLevel.ERROR)
        raise
    else:
        return (True, new_file_path)
