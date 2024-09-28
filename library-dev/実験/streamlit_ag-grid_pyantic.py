import streamlit as st
import pandas as pd
from pydantic import BaseModel, ValidationError, Field
from typing import List
from st_aggrid import AgGrid, GridUpdateMode
from st_aggrid.grid_options_builder import GridOptionsBuilder

# Pydanticモデルの定義
class Person(BaseModel):
    name: str = Field(..., min_length=2)
    age: int = Field(..., ge=0, le=120)
    email: str = Field(..., pattern=r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$")

# Excelファイルを読み込む関数
def load_excel(file):
    return pd.read_excel(file)

# データをバリデーションする関数
def validate_data(df):
    errors = []
    for index, row in df.iterrows():
        try:
            Person(**row.to_dict())
        except ValidationError as e:
            for error in e.errors():
                errors.append((index, error['loc'][0], str(error['msg'])))
    return errors

# メイン関数
def main():
    st.title("Excel Data Validator")

    # ファイルアップロード
    uploaded_file = st.file_uploader("Choose an Excel file", type="xlsx")
    if uploaded_file is not None:
        df = load_excel(uploaded_file)

        # バリデーション実行
        errors = validate_data(df)

        # エラーのあるセルにスタイルを適用
        cell_styles = []
        for error in errors:
            cell_styles.append({
                'rowIndex': error[0],
                'columnField': error[1],
                'cellStyle': {'backgroundColor': 'red', 'color': 'white'}
            })

        # AgGridオプションの設定
        gb = GridOptionsBuilder.from_dataframe(df)
        gb.configure_default_column(editable=True)
        grid_options = gb.build()

        # AgGridの表示
        grid_response = AgGrid(
            df,
            gridOptions=grid_options,
            update_mode=GridUpdateMode.VALUE_CHANGED,
            allow_unsafe_jscode=True,
            custom_css={
                ".ag-cell-invalid": {
                    "background-color": "red !important",
                    "color": "white !important"
                }
            }
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
