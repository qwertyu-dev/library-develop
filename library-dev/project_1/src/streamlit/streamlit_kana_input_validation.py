import streamlit as st
import pandas as pd
from pydantic import BaseModel, ValidationError, Field
from typing import Optional
from datetime import date
from st_aggrid import AgGrid, GridUpdateMode, JsCode
from st_aggrid.grid_options_builder import GridOptionsBuilder

from io import BytesIO

# ページのレイアウトを広げる設定
st.set_page_config(layout="wide")  # wideレイアウトを使用して幅を広げる

# Pydanticモデルの定義
# 各フォーマット用のPydanticモデルを定義
class HRModel(BaseModel):
    # 人事部フォーマット用のフィールドとバリデーション
    報告日: date
    no: int
    有効日付: date
    種類: str = Field(..., pattern=r"^(新規|変更|削除)$")  # `regex` -> `pattern` に修正
    対象: str
    部門コード: int
    親部店コード: int | None  # nullが許される場合
    部店コード: int | None
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

class InternationalModel(BaseModel):
    # 国際事務企画部フォーマット用のフィールドとバリデーション
    ...

class RelatedWithDummyModel(BaseModel):
    # 関連（ダミー課あり）フォーマット用のフィールドとバリデーション
    ...

class RelatedWithoutDummyModel(BaseModel):
    # 関連（ダミー課なし）フォーマット用のフィールドとバリデーション
    ...


# フォーマットとモデルのマッピング
format_models = {
    '人事': HRModel,
    '国企': InternationalModel,
    '関連(ダミー課あり):': RelatedWithDummyModel,
    '関連(ダミー課なし):': RelatedWithoutDummyModel,
}

# Excelファイルを読み込む関数
@st.cache_data
def load_excel(file) -> pd.DataFrame:
    return pd.read_excel(file)

# データをバリデーションする関数
def validate_data(df, model) -> list:
    def validate_row(index, row) -> list:
        try:
            model(**row.to_dict())
        except ValidationError as e:
            return [(index, error['loc'][0], str(error['msg'])) for error in e.errors()]
        else:
            return []

    return [error for index, row in df.iterrows() for error in validate_row(index, row)]

# バリデーションエラーを取得してスタイルを適用する関数
def get_invalid_cells(errors) -> dict:
    invalid_cells = {}
    for error in errors:
        row_idx, col, _ = error
        if row_idx not in invalid_cells:
            invalid_cells[row_idx] = []
        invalid_cells[row_idx].append(col)
    return invalid_cells

def add_katakana_column(_df):
    branch_name_column = next((col for col in _df.columns if '部店名' in col or '部店名称' in col), None)
    
    if branch_name_column:
        branch_name_index = _df.columns.get_loc(branch_name_column)
        
        if '部店カナ' not in _df.columns:
            _df.insert(branch_name_index + 1, '部店カナ', '')
        
        print(f"'{branch_name_column}'の右側に'部店カナ'Columnを追加しました。")
    else:
        print("部店名称のColumnが見つかりませんでした。")
    
    return _df

# メイン関数
def main() -> None:
    st.balloons()
    st.title("一括申請 Validator")

    # Initialize session state
    if 'selected_format' not in st.session_state:
        st.session_state.selected_format = None
    if 'uploaded_file' not in st.session_state:
        st.session_state.uploaded_file = None
    if 'file_uploader_key' not in st.session_state:
        st.session_state.file_uploader_key = 0

    # sideメニュー
    ## 部署選択
    new_selected_format = st.sidebar.radio(
        ':chicken: :rainbow[申請部署を選択]',
        list(format_models.keys()),
    )

    # Check if the selected format has changed
    if new_selected_format != st.session_state.selected_format:
        st.session_state.selected_format = new_selected_format
        st.session_state.uploaded_file = None
        st.session_state.file_uploader_key += 1  # Increment the key to force re-render

    st.sidebar.markdown('---')

    ## ファイルアップロード
    uploaded_file = st.sidebar.file_uploader(
        ":chicken: :rainbow[チェック対象Excelファイル選択]",
        type="xlsx",
        key=f"file_uploader_{st.session_state.file_uploader_key}"
    )

    if uploaded_file is not None:
        # Store the uploaded file in session state
        st.session_state.uploaded_file = uploaded_file

        # sideメニューからの情報を反映
        st.markdown('---')
        st.subheader(f"申請部署区分: {st.session_state.selected_format}")
        st.info(f"申請ファイル名: {uploaded_file.name}")

        # 使用例
        _df = load_excel(uploaded_file)
        _df = add_katakana_column(_df)

        # 選択部署からのmodelマッピング結果
        selected_model = format_models[st.session_state.selected_format]

        # バリデーション実行
        errors = validate_data(_df, selected_model)
        invalid_cells = get_invalid_cells(errors)

        # AgGridオプションの設定
        gb = GridOptionsBuilder.from_dataframe(_df)
        gb.configure_default_column(editable=False)
        gb.configure_column("部店カナ", editable=True)

        # 横幅を自動調整 (flex を使って)
        for col in _df.columns:
            gb.configure_column(col, flex=1, minWidth=125)  # flex=1で自動フィット、minWidthで最小幅を設定

        # カスタムのJavaScriptコードを使用してエラーハイライトを設定
        cell_style_jscode = JsCode("""
        function(params) {
            const invalidCells = %s;
            if (invalidCells[params.node.rowIndex] &&
                invalidCells[params.node.rowIndex].includes(params.colDef.field)) {
                return {
                    'color': 'green',
                    'backgroundColor': 'yellow',
                };
            }
            return {};
        }
        """ % invalid_cells)

        # 各列に対してスタイルを適用
        for col in _df.columns:
            gb.configure_column(col, cellStyle=cell_style_jscode)

        # 設定確定
        grid_options = gb.build()

        # AgGridの表示
        grid_response = AgGrid(
            _df,
            gridOptions=grid_options,
            update_mode=GridUpdateMode.VALUE_CHANGED,
            allow_unsafe_jscode=True,
            fit_columns_on_grid_load=True,  # カラムが自動で画面にフィット
            height=150,                     # グリッドの高さ
            width="1000",                   # グリッド全体の幅を1000に設定
        )

        # エラーメッセージの表示
        st.subheader(f"Validationチェック結果: {st.session_state.selected_format}一括申請")
        if errors:
            st.error(f"Validation Errorがあります: {len(errors)}か所")
            for error in errors:
                st.write(f"Row {error[0]+1}, Column '{error[1]}': {error[2]}")
        else:
            st.success("No validation errors found.")

        st.markdown('---')
        st.subheader("部店カナ入力結果 Excelダウンロード")
        st.info('Validationエラーなし、部店カナ入力(必要に応じて)完了後にダウンロードしてください')
        st.caption('- 部店カナ入力は必ずしも必須ではありません、人が判断してください')
        st.caption('- ダウンロードしたExcelファイルにより、人事部宛に部店カナ名の承認依頼を行ってください')

        # ダウンロードボタン
        grid_response['data'].to_excel(buf := BytesIO(), index=False)
        st.download_button(
            "Excelファイル: Download",
            buf.getvalue(),
            uploaded_file.name,
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )

if __name__ == "__main__":
    main()
