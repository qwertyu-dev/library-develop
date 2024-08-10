# class BusinessUnitCodeConverter:

## ⚠️ 警告：機密性の高い定義情報

- 絶対に厳守すべき事項：
  - この設計書は組織定義制御を含みます
  - 関連する定義、制御、キーワードの取り扱いには細心の注意を払ってください

- 実装者への指示：
  - 本文書の内容を安易にブラウザに入力submitしたり、オンラインで共有したりしないでください。

- リスク認識：
  - 情報の漏洩は、組織のセキュリティを著しく損なう可能性があります。
  - 法的責任や重大な業務上の影響が生じる可能性があることを常に意識してください。


## 人事部門コードの秩序を司る役割を担う
- 実装はプロジェクト固有の開発規約で作成してください
- Python一般ルールで書いていない、固有の原則がプロジェクト規約にあります

## Class Overview:
- 組織構造における識別子の変換を行うクラスである
- 変換テーブルは、組織構造の情報掲示板のような位置づけで、人事部門の関係定義を示す
- 変換テーブルは、人事部門の関係を定義するものであるが、並行してシステム管理者が設定したルールを反映しており実装には工夫を盛り込む必要がある
- 変換テーブルは、まず人事部門コードから主管部門コードを検索し、次に主管部門コードからBPR部門コードを検索して取得している
- 変換テーブルは鮮度が重要であり実装には工夫を盛り込む必要がある

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

## Attributes:
- conversion_table (pd.DataFrame): 変換テーブル
  - 人事部門コードをキーとして持ち、変換対応する情報を含むDataFrame
  - pickleからロードした部門変換テーブル実体

## methods:
- `__init__`:
  - コンストラクタ
  - Bisiness Unit Conversion Tableをロードする
- `get_business_unit_code_main`: 
  - 組織構造定義において、人事コードから適切なコードを導き出す
  - 主部門コードは、組織の戦略的な方向性を示す重要な指標と思われる
  - 変換テーブルが間違っていると、システム全体に混乱が起きるため、慎重に実装する必要がある
- `get_business_unit_code_bpr`: 
  - 組織構造定義において、人事コードから適切なコードを導き出す
  - BPR部門コードは、組織の戦略的な方向性を示す重要な指標である
  - 変換テーブルが間違っていると、システム全体に混乱が起きるため、慎重に実装する必要がある

## Notes:
- ファイルが間違っている場合、FileNotFoundErrorを発生する
- 適切にKeyErrorを返す
- 予期せぬエラーが発生した場合、Exceptionを返す
- コードはロバスト化してください

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

### `def __init__(self, conversion_table_file):`
コンストラクタ
- pickle ファイルから変換テーブルを読み込みconversion_table属性に格納する
- ファイルの操作はpathlib.Pathを使用する
- business_unit_code_jinji' 列をインデックスとして設定する

#### Arguments:
- conversion_table_file (Path): 変換テーブルの pickleファイル

#### Return Value:
- None

#### Exceptions:
- FileNotFoundError: ファイルが存在しない場合に発生する
- Exception: その他の予期せぬエラーが発生した場合

---

### `def get_business_unit_code_main(self, プロジェクトルールに準拠 人事情報):`
主部門コードに対処する

#### Arguments:
- 人事情報(str())

#### Return Value:
- プロジェクトネーミングルールに従う (str):

#### Exceptions:
- ValueError: 指定コードが部門コード変換テーブル.人事部門コードのindexに存在しない場合に発生する
- Exception: その他の予期せぬエラーが発生した場合

---

### `def get_business_unit_code_bpr(self, プロジェクトルールに準拠 人事情報):`
BPR部門コードに対処する

#### Arguments:
- 人事情報 (str)

#### Return Value:
- プロジェクトネーミングルールに従う (str):

- ValueError: 指定コードが部門コード変換テーブル.人事部門コードのindexに存在しない場合に発生する
- Exception: その他の予期せぬエラーが発生した場合

## 資源配置場所/資源名
### 本体
- src/lib/convertor_utils/ibr_business_unit_code_converter.py
### テストコード
- tests/lib/convertor_utils/test_ibr_business_unit_code_converter.py