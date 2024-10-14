"""Excelファイル取得サポートライブラリ"""
import sys
import traceback
from pathlib import Path

import pandas as pd

from src.lib.common_utils.ibr_dataframe_helper import tabulate_dataframe

# config共有
from src.lib.common_utils.ibr_decorator_config import (
    initialize_config,
)
from src.lib.common_utils.ibr_enums import LogLevel

config = initialize_config(sys.modules[__name__])
log_msg = config.log_message

################################
# class
################################
class ExcelDataLoaderError(Exception):
    """カスタム例外"""
class ExcelDataLoader:
    """ExcelBookをDataFrameに取り込むサポートライブラリ

    ExcelからDataFrameへの取り込みサポート機能

    Args:
        file_path: (str|Path), ExcelBookファイルへのパス
        skiprows: (int), default=0, Excelシート状の読み飛ばし行
        usecols: (list[int]|None), default=None, DataFrameに取り込むColumn番号
        exclusion_sheets: (list[str]|None), default=None, 取り込まないSheet名


    Changelog:
        - v1.0.0 (2024/01/01): Initial release
        -
    """
    def __init__(
        self,
        file_path: str|Path,
    ):
        self.file_path = Path(file_path)

    # 個別例外定義
    def function_select_error(self) -> None:
        """単にValueErrorを定義したもの"""
        raise ValueError

    def read_excel_one_sheet(self, sheet_name: str, skiprows: int=0, skiprecords: int=0, usecols: list[int]|None=None) -> pd.DataFrame|None:
        """ExcelBookからシート1枚を指定してDataFrameへ取り込み

        1つのSheetからDataFrameへ取り込みを行う
        属性は全てobject型で取り込み、利用者側で必要に応じて型変換対応を行う

        Copy right:
            (あとで書く)

        Args:
            sheet_name (str): 読み込むシート名
            skiprows (int): default=0 読み飛ばすExcel行数
            skiprecords (int): default=0 読み飛ばすDataFrame行数,DataFrame取り込み後の処理
            usecols (list[int | None]): default=None 取得する列番号

        Returns:
            (pd.DataFrame|None): Sheetから取り込んだDataFrame

        Raises:
            - FileNotFoundError
            - PermissionError
            - IsADirectoryError
            - pd.errors.ParserError
            - pd.errors.EmptyDataError
            - MemoryError
            - Exception

        Example:
            >>> data_loader = ExcelDataLoader('./test.xlsx')
            >>> data_loader.read_excel_one_sheet('Sheet1')

        Notes:
            parse()処理でskiprowsは行わずDataFrameに取り込んだ後で行飛ばしを行う

        Changelog:
            - v1.0.0 (2024/01/01): Initial release
            -
        """
        try:
            with pd.ExcelFile(self.file_path) as target_excel:
                if sheet_name not in target_excel.sheet_names:
                    return pd.DataFrame()

                _df =  target_excel.parse(
                    sheet_name=sheet_name,
                    index_col=None, # 余計なColを自動生成させない
                    na_values='',
                    skiprows=skiprows,
                    header=0,
                    usecols=usecols,
                    dtype=object,     # デフォルトでは全てobject型で取り込み
                )
                # skiprowsは個別に対応する
                _df = _df.iloc[skiprecords:]
                log_msg(f'\nSheet_name: {sheet_name}\n{tabulate_dataframe(_df)}', LogLevel.DEBUG)
                return _df.reset_index(drop=True)
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
            log_msg(f'Not enough memory to read Excel file: {e}', LogLevel.ERROR)
            raise
        except Exception as e:
            tb = traceback.TracebackException.from_exception(e)
            log_msg(''.join(tb.format()), LogLevel.ERROR)
            raise ExcelDataLoaderError from e


    def read_excel_all_sheets(self, skiprows: int=0, skiprecords: int=0, usecols: list[int]|None=None, exclusion_sheets: list[str]|None=None) -> pd.DataFrame|None:
        """ExcelBookからシート1枚を指定してDataFrameへ取り込み

        複数のSheetからDataFrameへ取り込みを行う

        Copy right:
            (あとで書く)


        Args:
            skiprows (int): default=0 読み飛ばすExcel行数
            skiprecords (int): default=0 読み飛ばすDataFrame行数,DataFrame取り込み後の処理
            usecols (list[int | None]): default=None 取得する列番号
            exclusion_sheets (list[str] | None): default=None 取り込まないシート名のリスト

        Returns:
            (pd.DataFrame|None): Sheetから取り込んだDataFrame

        Raises:
            - FileNotFoundError
            - PermissionError
            - IsADirectoryError
            - pd.errors.ParserError
            - pd.errors.EmptyDataError
            - MemoryError
            - Exception

        Example:
            >>> data_loader = ExcelDataLoader('./test.xlsx')
            >>> data_loader.read_excel_all_sheets()

        Notes:
            read_excel_one_sheet()で例外処理をハンドリングしているため
            取り込み処理フェーズではExceptionのみ設定している。

        Changelog:
            - v1.0.0 (2024/01/01): Initial release
            -
        """
        # Noneの場合は空listに差し替える
        if exclusion_sheets is None:
            exclusion_sheets = []

        try:
            with pd.ExcelFile(self.file_path) as target_excel:
                if len(target_excel.sheet_names) == 1:
                    log_msg('BookのSheet数が1枚の場合は read_excel_one_sheet()を使用してください', LogLevel.ERROR)
                    # raise ValueError Ruff TRY301
                    _ = self.function_select_error()
                all_sheets = {sheet_name: self.read_excel_one_sheet(sheet_name=sheet_name, skiprows=skiprows, skiprecords=skiprecords,  usecols=usecols) \
                    for sheet_name in target_excel.sheet_names if sheet_name not in exclusion_sheets}

                # 各シートのデータフレームに対してreset_index(drop=True)を適用
                all_sheets = {sheet_name: df.reset_index(drop=True) for sheet_name, df in all_sheets.items()}

                # empty判定
                log_msg(f'all_sheets: {all_sheets}', LogLevel.DEBUG)
                if not all_sheets:
                    return pd.DataFrame()

                # 全DataFrameのcolumns数が一致判定
                #base_df_columns = list(all_sheets.values())[0].columns
                base_df_columns = next(iter(all_sheets.values())).columns

                # すべてのDataFrameの列が一致するか確認
                for df in list(all_sheets.values())[1:]:
                    if not df.columns.equals(base_df_columns):
                        return pd.DataFrame()

                # concatを実行
                df_cum_excel = pd.concat(list(all_sheets.values()), axis=0, ignore_index=True)
                log_msg(f'df_cum_excel: {df_cum_excel}', LogLevel.DEBUG)

        except pd.errors.EmptyDataError as e:
            log_msg(f'EmptyDataError: {e}', LogLevel.ERROR)
            tb = traceback.TracebackException.from_exception(e)
            log_msg(''.join(tb.format()), LogLevel.ERROR)
            raise
        except Exception as e:
            tb = traceback.TracebackException.from_exception(e)
            log_msg(''.join(tb.format()), LogLevel.ERROR)
            #raise
            raise ExcelDataLoaderError from e

        return df_cum_excel

    # ErrorManagerに役割を移譲しました 202407/7
    # TODO(suzuki) Delete

    #def logger_validation_errors(self, errors: list[list[int, dict[str, Any]]], log_level: enumerate = LogLevel.ERROR) -> None:
    #    """ExcelデータValidator結果出力ヘルパー

    #    validationエラー結果をerrors listから取得しカスタムロガーに出力する

    #    入力サンプル
    #        validation errors: [
    #            (0, [
    #                {'type': 'int_type', 'loc': ('e',), 'msg': 'Input should be a valid integer', 'input': 'あ', 'url': 'https://errors.pydantic.dev/2.5/v/int_type'},
    #                {'type': 'string_type', 'loc': ('g',), 'msg': 'Input should be a valid string', 'input': 1, 'url': 'https://errors.pydantic.dev/2.5/v/string_type'},
    #                ]),
    #            (1, [
    #                {'type': 'int_type', 'loc': ('d',), 'msg': 'Input should be a valid integer', 'input': 's', 'url': 'https://errors.pydantic.dev/2.5/v/int_type'}
    #                ])
    #            ]
    #    出力サンプル:
    #        Validation error at (1, e):  Input should be a valid integer, wrong values: あ

    #    Copy right:
    #        (あとで書く)

    #    Args:
    #        errors (list[list[dict[str, Any]]]): validatorエラーを格納したlist
    #        log_level (enumerate): default=LogLevel.ERROR, デフォルトはエラー扱いでカスタムロガー出力

    #    Returns:
    #        ...

    #    Raises:
    #        - _description_

    #    Example:
    #        >>> # ExcelDataLoaderインスタンス生成済とする
    #        >>> data_loader = ExcelDataLoader('./test.xlsx')
    #        >>> # validatorエラーを蓄積したlistを渡す
    #        >>> data_loader.logger_validation_errors(validate_errors)

    #    Notes:
    #        instance生成パラメータに対する依存性はないものの
    #        packageのmain.__init__()処理でExcelDataLoader()インスタンス生成を行う想定としており
    #        Excel取り込み処理と必ず連動する規約としているのでinstance メソッドの扱いとする

    #    Changelog:
    #        - v1.0.0 (2024/01/01): Initial release
    #        -
    #    """
    #    # エラー有無チェック
    #    if not errors or len(errors) == 0:
    #        log_msg('No validation errors', LogLevel.INFO)
    #        return

    #    log_msg(f'errors: {errors}', LogLevel.DEBUG)
    #    for _, error in enumerate(errors):
    #        # エラー発生行を取得
    #        error_row = error[0]

    #        # エラー発生行の各エラーー取得(1行に複数あり想定)
    #        for _, error_dict in enumerate(error[1]):
    #            log_msg(f'error_dict: {error_dict}', LogLevel.DEBUG)

    #            # 想定外有無チェック
    #            if not isinstance(error_dict, dict):
    #                log_msg(f'Unexpected error format at row {error_row + 1}', log_level)
    #                continue

    #            # 出力項目編集
    #            keys = ['msg', 'loc', 'input']
    #            values = [error_dict.get(key, None) for key in keys]
    #            log_msg(f'values: {values}', LogLevel.DEBUG)

    #            # 出力項目取得結果チェック
    #            if None in values:
    #                log_msg(f'values: {values}', log_level)
    #                continue

    #            # logger出力
    #            # エラー発生位置 DataFrame(行, 列): エラー理由, エラー値
    #            # values: ['Input should be a valid string', ('g',), 1]:
    #            log_msg(f'Validation error at ({error_row + 1}, {values[1][0]}):  {values[0]}, wrong values: {values[2]}', log_level)
    #    return
