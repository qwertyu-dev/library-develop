# class BusinessUnitCodeConverter:

## 人事部門コードの変換を行うクラス

## ClassOverView:
- 人事部門コードをキーとして、変換テーブルから対応する主管部門コード及びBPR部門コードを取得する

## Business Unit Conversion Table 
- business_unit_code_table.pickle ファイルから読み込まれる
- 引数としてのパス操作はPathオブジェクトで対処する

### Table Structure

#### Table Overview
- レイアウト定義: `部門変換テーブル`を参照すること

| 項目 | 説明 |
|------|------|
| **ファイル名** | business_unit_code_table.pickle |
| **属性** | DataFrame/pickle |

#### Column Definition 

| No | Column名称(日本語) | column_name(python) | 桁数/文字数 | データ型 |
|----|--------------------|---------------------|-------------|----------|
| 1  | 人事部門コード | business_unit_code_jinji | - | str |
| 2  | 人事部門名 | business_unit_name_jinji | - | str |
| 3  | 主管部門コード | main_business_unit_code_jinji | - | str |
| 4  | BPR部門コード | business_unit_code_bpr | - | str |
| 5  | BPR部門名称 | business_unit_name_bpr | - | str |


## Attributes:
- conversion_table (pd.DataFrame): 変換テーブル
  - 人事部門コードをキーとして持ち、変換対応する情報を含むDataFrame
  - pickleからロードした部門変換テーブル実体

## methods:
- `__init__`:
  - コンストラクタ
  - Bisiness Unit Conversion Tableをロードする
- `get_business_unit_code_main`: 
  - 人事部門コードから主管部門コードを取得する
- `get_business_unit_code_bpr`: 
  - 人事部門コードからBPR部門コードを取得する

## Usage Example:
```python
from pathlib import Path
import pandas as pd

# 共通関数配置位置から相対importを使用してBusinessUnitCodeConverterを取得してください
converter = BusinessUnitCodeConverter(Path(business_unit_code_table.pickle))

business_unit_code_main = converter.get_business_unit_code_main("Z1")
# print(business_unit_code_main)
# A1

business_unit_code_bpr = converter.get_business_unit_code_bpr("Z1")
# print(business_unit_code_bpr)
# 653 
```

## Notes:
- 変換テーブルは business_unit_code_table.pickle ファイルから読み込まれるため、ファイルが存在し、pickle形式で保存されている必要がある
- ファイルパスが間違っている場合、FileNotFoundErrorを発生する
- 引数指定した人事部門コードが変換テーブルに存在しない場合、KeyErrorを返す
- 予期せぬエラーが発生した場合、Exceptionを返す

## Dependency:
- pickle
- pandas
- pathlib

## Chage History:
| No | 修正理由 | 修正点 | 対応日 | 担当 |
|----|----------|--------|--------|------|
| v0.1 | 初期定義作成 | 新規作成 | 2024/07/20 | xxxx aaa.bbb |

---

## Method Definitions

### `def __init__(self, conversion_table_file: Path) -> None:`
コンストラクタ
- pickle ファイルから変換テーブルを読み込みconversion_table 属性に格納する
- ファイルパスの操作はpathlib.Pathを使用する
- business_unit_code_jinji' 列をインデックスとして設定する

#### Arguments:
- conversion_table_file (Path): 変換テーブルの pickle ファイルパス

#### Return Value:
- None

#### Exceptions:
- FileNotFoundError: ファイルが存在しない場合に発生する
- Exception: その他の予期せぬエラーが発生した場合

---

### `def get_business_unit_code_main(self, bisiness_unit_code_jinji: str) -> str:`
- 部門コード変換テーブルのindexを人事部門コード検索し合致しなければValueErrorを発生しアーリーリターンを行う
- 人事部門コードから主管部門コードを取得する

#### Arguments:
- bisiness_unit_code_jinji (str): 人事部門コード

#### Return Value:
- str: 人事部門コードに対応する主管部門コード

#### Exceptions:
- ValueError: 指定コードが部門コード変換テーブル.人事部門コードのindexに存在しない場合に発生する
- Exception: その他の予期せぬエラーが発生した場合
---

### `def get_business_unit_code_bpr(self, bisiness_unit_code_jinji: str) -> str:`
- 部門コード変換テーブルのindexを人事部門コード検索し合致しなければValueErrorを発生しアーリーリターンを行う
- 人事部門コードからBPR部門コードを取得する

#### Arguments:
- bisiness_unit_code_jinji (str): 人事部門コード

#### Return Value:
- str: 人事部門コード対応するBPR部門コード

#### Exceptions:
- ValueError: 指定コードが部門コード変換テーブル.人事部門コードのindexに存在しない場合に発生する
- Exception: その他の予期せぬエラーが発生した場合


## 資源配置場所/資源名
### 本体
- src/lib/convertor_utils/ibr_business_unit_code_converter.py
### テストコード
- tests/lib/convertor_utils/test_ibr_business_unit_code_converter.py