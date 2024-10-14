"""DataFrame操作サポートライブラリ"""

import sys
import traceback

import pandas as pd
from tabulate import tabulate

# config共有
from src.lib.common_utils.ibr_decorator_config import (
    initialize_config,
)
from src.lib.common_utils.ibr_enums import LogLevel

config = initialize_config(sys.modules[__name__])
log_msg = config.log_message

################################
# 関数定義
################################
def _tabulate_wrapper(df, headers, tablefmt) -> str:
    """tabulate出力ヘルパー関数"""
    return tabulate(df, headers=headers, tablefmt=tablefmt)

def tabulate_dataframe(df: pd.DataFrame, headers: list|None=None, tablefmt:str|None=None) -> str:
    """DataFrame出力サポート

    tabulateを使用してDataFrame出力サポートを行う

    Args:
        df (pd.Dataframe): 出力対象DataFrame
        headers (list, optional): tabulate keyパラメータ,指定なければ'keys'を設定する
        tablefmt(str, optional): tabulateテーブルフォーマット,指定なければ'pipe'を設定する

    Returns:
        str: テキスト編集結果、その後logger出力を呼び出し側で実施する

    Raises:
        Exception: tabulate処理で何らかの失敗発生

    Notes:
        df自体への編集処理は行っていないことから_df = df.copy()は行わない

    """
    if not headers:
        headers = 'keys'
    if not tablefmt:
        tablefmt = 'pipe'

    if isinstance(headers, list) and (len(list(df.columns)) != len(headers)):
        log_msg(f'DataFrame.columns: {df.columns}', LogLevel.ERROR)
        log_msg(f'headers: {headers}', LogLevel.ERROR)
        msg = 'DataFrame.columnsとheadersの列数は一致している必要があります'
        log_msg(f'{msg}', LogLevel.ERROR)
        raise ValueError(msg)

    try:
        output = _tabulate_wrapper(
        df,
        headers=headers,
        tablefmt=tablefmt,
        )
    except Exception as e:
        tb = traceback.TracebackException.from_exception(e)
        log_msg(''.join(tb.format()), LogLevel.ERROR)
        raise
    else:
        log_msg(f'\n{output}', LogLevel.DEBUG)
        return output
