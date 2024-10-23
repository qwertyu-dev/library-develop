import pandas as pd

from src.lib.common_utils.ibr_enums import LogLevel
from src.model.factory.editor_factory import EditorFactory

# config共有
import sys
from src.lib.common_utils.ibr_decorator_config import initialize_config
config = initialize_config(sys.modules[__name__])
log_msg = config.log_message

# モジュール例外
class CreateEditorFactoryError(Exception):
    pass
class ProcessRowError(Exception):
    pass

class ImportFacadeNullError(Exception):
    pass

def create_editor_factory(decision_table: pd.DataFrame, import_facade: str) -> EditorFactory:
    """EditorFactoryインスタンスを生成するだけの役割

    どのFacade(Editor)を呼出・動的生成の決定,現状では受付?パターン編集?
    EditorFactory.create_editor()
    """
    if not import_facade:
        err_msg = f'import_facade is null: {import_facade}'
        raise ImportFacadeNullError(err_msg) from None
    # contollerサポート
    config.log_message(f'import facade: {import_facade}', LogLevel.INFO)
    try:
        return EditorFactory(decision_table, import_facade)
    except Exception as e:
        err_msg = f'EditorFactory生成に失敗しました: {import_facade}'
        raise CreateEditorFactoryError(err_msg) from e


# TODO(suzuki): output_layoutを引数追加、mainからの呼び出し対応
def process_row(row: pd.Series, factory: EditorFactory, output_layout: list[str]) -> pd.Series:
#def process_row(row: pd.Series, factory: EditorFactory) -> pd.Series:
    """データ編集処理を実行する"""
    if not isinstance(row, pd.Series):
        err_msg = f'rowはpd.Seriesでなければなりません: {row}'
        raise ProcessRowError(err_msg) from None

    if row.empty:
        err_msg = f'空のrowは許容されません: {row}'
        raise ProcessRowError(err_msg) from None

    # output_layoutに関するチェックを追加
    if output_layout is None:
        err_msg = f'空のlayout定義は許容されません: {output_layout}'
        raise ProcessRowError(err_msg) from None

    if len(output_layout) == 0:
        err_msg = f'空のlayout定義は許容されません: {output_layout}'
        raise ProcessRowError(err_msg) from None


    # contollerサポート
    try:
        # Editor生成
        editor = factory.create_editor(row)

        # TODO(suzuki):editorにoutput 定義を渡す
        log_msg(f'output layout: {output_layout}', LogLevel.INFO)
        editor.output_columns = output_layout

        # Seriesに対する編集処理呼び出し
        return editor.edit_series(row)
    except Exception as e:
        err_msg = f'column編集に失敗しました row: {row}'
        raise ProcessRowError(err_msg) from e
