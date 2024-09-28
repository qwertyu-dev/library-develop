import streamlit as st
import pandas as pd
from pydantic import BaseModel, ValidationError, Field
from typing import Optional
from datetime import date
from st_aggrid import AgGrid, GridUpdateMode, JsCode
from st_aggrid.grid_options_builder import GridOptionsBuilder

# ページのレイアウトを広げる設定
st.set_page_config(layout="wide")  # wideレイアウトを使用して幅を広げる

# Pydanticモデルの定義
class ReportModel(BaseModel):
    報告日: date
    no: int
    有効日付: date
    種類: str = Field(..., pattern=r"^(新規|変更|削除)$")  # `regex` -> `pattern` に修正
    対象: str
    部門コード: int
    親部店コード: Optional[int]  # nullが許される場合
    部店コード: Optional[int]
    部店名称: str
    部店名称英語: Optional[str] = Field(None, max_length=100)  # 長さ制限
    課_エリアコード: Optional[int]
    課_エリア名称: str
    課_エリア名称英語: Optional[str]
    常駐部店コード: Optional[int]
    常駐部店名称: Optional[str]
    純新規店の組織情報受渡し予定日開店日基準: Optional[date]
    共通認証受渡し予定日人事データ反映基準: Optional[date]
    備考: Optional[str]

# Excelファイルを読み込む関数
def load_excel(file):
    return pd.read_excel(file)

# データをバリデーションする関数
def validate_data(df):
    errors = []
    for index, row in df.iterrows():
        try:
            ReportModel(**row.to_dict())
        except ValidationError as e:
            for error in e.errors():
                errors.append((index, error['loc'][0], str(error['msg'])))
    return errors

# バリデーションエラーを取得してスタイルを適用する関数
def get_invalid_cells(errors):
    invalid_cells = {}
    for error in errors:
        row_idx, col, _ = error
        if row_idx not in invalid_cells:
            invalid_cells[row_idx] = []
        invalid_cells[row_idx].append(col)
    return invalid_cells

# メイン関数
def main():
    st.title("Excel Data Validator")

    # ファイルアップロード
    uploaded_file = st.file_uploader("Choose an Excel file", type="xlsx")
    if uploaded_file is not None:
        df = load_excel(uploaded_file)

        # バリデーション実行
        errors = validate_data(df)
        invalid_cells = get_invalid_cells(errors)

        # AgGridオプションの設定
        gb = GridOptionsBuilder.from_dataframe(df)
        gb.configure_default_column(editable=True)

        # 横幅を自動調整 (flex を使って)
        for col in df.columns:
            gb.configure_column(col, flex=1, minWidth=125)  # flex=1で自動フィット、minWidthで最小幅を設定


        # カスタムのJavaScriptコードを使用してエラーハイライトを設定
        cell_style_jscode = JsCode("""
        function(params) {
            const invalidCells = %s;
            if (invalidCells[params.node.rowIndex] && 
                invalidCells[params.node.rowIndex].includes(params.colDef.field)) {
                return {
                    'color': 'white',
                    'backgroundColor': 'red'
                };
            }
            return {};
        }
        """ % invalid_cells)

        # 各列に対してスタイルを適用
        for col in df.columns:
            gb.configure_column(col, cellStyle=cell_style_jscode)

        grid_options = gb.build()

        # AgGridの表示
        grid_response = AgGrid(
            df,
            gridOptions=grid_options,
            update_mode=GridUpdateMode.VALUE_CHANGED,
            allow_unsafe_jscode=True,
            fit_columns_on_grid_load=True,  # これによりカラムが自動で画面にフィット
            height=400,                     # グリッドの高さ
            width="1000"                    # グリッド全体の幅を100%に設定
        )

        # エラーメッセージの表示
        if errors:
            st.error("Validation Errors:")
            for error in errors:
                st.write(f"Row {error[0]+1}, Column '{error[1]}': {error[2]}")
        else:
            st.success("No validation errors found.")

if __name__ == "__main__":
    main()

