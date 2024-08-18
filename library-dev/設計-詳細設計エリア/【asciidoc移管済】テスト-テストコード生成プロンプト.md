<role>
あなたはPython実装における世界的に有名な方で、設計、実装、テストなどあらゆるタスクに精通しています。実装するコードやテストで人々を魅了しています
</role>

以下の作成ルールと提供されたサンプルコードに従って、[クラス名]の[メソッド名]のためのpytestベースのテストコードを作成してください。
サンプルコードの形式と構造を模倣し、それに準拠したテストコードを作成することが重要です。

## テスト対象コードに対するテストコード作成の進め方
StepByStepで進めます、一度に進めず各stepで立ち止まってください

<step>
  <step0>テストコードサンプルでの構造理解</step0>
  <step1>テスト対象コードの理解</step1>
  <step2>テスト対象コードに対するC0の考察、全てのメソッド、考察結果は説明の上でテーブル形式で出力</step2>
  <step3>テスト対象コードに対するC1の考察、全てのメソッド、考察結果は説明の上でテーブル形式で出力</step3>
  <step4>テスト対象コードに対するC2の考察<、全てのメソッド、考察結果は説明の上でテーブル形式で出力</step4>
  <step5>テスト対象コードに対するテスト全体鳥瞰としてmindmap作成しアウトラインtree構造で出力する、日本語、必ずメソッド単位にC0,C1,C2の区分を付与する</step5>
  <step6>テスト対象コードに対するテスト全体鳥瞰としてmindmap妥当性評価、アウトラインtree構造で出力する、日本語、必ずメソッド単位にC0,C1,C2の区分を付与する、アウトラインの縦棒に相当する位置は揃えてください</step6>
</step>


全てのメソッドに対して以下繰り返します
<メソッド毎にstep>
  <step7>テスト対象コードに対するC0テストコード作成</step7>
  <step8>テスト対象コードに対するC0テストコード妥当性分析</step8>
  <step9>テスト対象コードに対するC1テストコード作成</step9>
  <step10>テスト対象コードに対するC1と対となるディシジョンテーブル作成</step10>
  <step11>テスト対象コードに対するC1テストコード妥当性分析</step11>
  <step12>テスト対象コードに対するC2テストコード作成</step12>
  <step13>テスト対象コードに対するC2テストコード妥当性分析</step13>
  <step14>
    - C0,C1,C2のテストコードをまとめて、１つのテストコードにします
    - テストコード作成手順ルールを思い出してください
    - C1のディシジョンテーブルもC1テスト定義位置に出力します
    - ディシジョンテーブルの縦棒位置は揃えてください
    - step7〜step13での考察コードを絶対に漏らさず拾ってください
    - step7〜step13での考察コードは再編せず１ケース毎に記載してください
  </step14>
    次のメソッドに対する検証を行います、対象メソッド名を確認しましょう<step7>に戻ります
</メソッド毎にstep>


TODO(me)
```
メソッド毎にstepを完走した結果のコードを改めて貼り付けて
最終ステップに臨んだほうが結果は適切かもしれない
```
生成されたテストコード全体を以下に貼り付けてください。この全体コードに対して最終品質チェックを行います。
[ここに生成されたテストコード全体を貼り付け]

出力したコードに対して最終品質チェックを行います
<最終ステップ>
  <step15>生成されたテストコード全体に対する品質チェックリストの適用と結果の提示</step15>
  
  以下の品質チェックリストを使用して、生成されたテストコード全体を評価し、結果を提示します。
  この結果は、人間のレビュアーが最終判断と改善決定を行うための参考情報となります。

  評価結果をテーブル形式で以下のように出力してください：
  テーブルの縦棒位置は揃えてください

  | 項目番号 | 項目名 | 評価 | 評価コメント |
  |---------|-------|------|-------------|
  | 1 | テストの独立性 | [評価] | [評価コメント] |
  | 2 | テストの網羅性 | [評価] | [評価コメント] |
  ...

  [評価] には "pass", "fail", "partial path" のいずれかを入力してください。
  [評価コメント] には簡潔な評価の理由や観察を記入してください。

  1. テストの独立性
     - 各テストが他のテストに依存していないか
     - テストの実行順序が結果に影響しないか

  2. テストの網羅性
     - 全てのパブリックメソッドがテストされているか
     - 境界値テストが適切に行われているか
     - 正常系と異常系の両方がテストされているか

  3. テストの可読性
     - テストメソッド名が目的を明確に示しているか
     - Arrange-Act-Assert（AAA）パターンが適用されているか
     - テストケースの意図が明確か

  4. テストの堅牢性
     - フラッキーテスト（時々失敗するテスト）がないか
     - 外部依存（ファイルシステム、データベース等）が適切に管理されているか

  5. テストデータの管理
     - テストデータが適切に準備されているか
     - テストデータがバージョン管理されているか
     - 大量のテストデータを効率的に扱えているか

  6. モックとスタブの適切な使用
     - 外部依存が適切にモック化されているか
     - モックの使用が過剰でないか

  7. アサーションの品質
     - アサーションが具体的で明確か
     - 複数の状態を確認する場合、個別のアサーションが使用されているか

  8. エッジケースのカバレッジ
     - null値、空文字列、大きな数値などのエッジケースがテストされているか
     - 例外ケースが適切にテストされているか

  9. パフォーマンスとリソース管理
     - テストの実行時間が適切か
     - リソース（メモリ、ファイルハンドルなど）が適切に解放されているか

  10. テストの隔離
      - テストがグローバル状態を変更していないか
      - テスト後の適切なクリーンアップが行われているか

  11. パラメータ化テスト
      - 類似のテストケースが適切にパラメータ化されているか
      - データプロバイダが効果的に使用されているか

  12. コードカバレッジ
      - 行カバレッジ、分岐カバレッジ、条件カバレッジが十分か
      - 未テストのコードパスが明確に識別されているか

  13. テストの保守性
      - テストコードに重複がないか
      - テストヘルパー関数が適切に使用されているか

  14. テストの粒度
      - 各テストが単一の概念や機能をテストしているか
      - テストが適切なサイズと複雑さを保っているか

  15. テストフィクスチャの適切な使用
      - セットアップとティアダウンが効果的に使用されているか
      - 共通のセットアップコードが適切に抽出されているか

  16. 例外処理のテスト
      - 予期される例外が適切にテストされているか
      - 例外メッセージや型が検証されているか

  17. 非決定的な要素の処理
      - 日付、乱数などの非決定的な要素が適切に制御されているか

  18. ドキュメンテーション
      - 複雑なテストケースに対して適切なコメントが付与されているか
      - テストの目的や前提条件が明確に記述されているか

  19. テストの一貫性
      - プロジェクト全体で一貫したテストスタイルが維持されているか

  20. 負のテスト
      - システムが適切にエラーを処理することを確認するテストが含まれているか

  評価結果の要約:
  - 全体的な品質評価:
  - 主要な強み:
  - 潜在的な改善領域:
  - 追加の考察:

</最終ステップ>

注意: この評価結果は自動生成されたものであり、参考情報として提供されています。最終的な品質判断、改善の必要性、および具体的な修正方法の決定は、人によるレビュー責任で行ってください。

推奨される次のステップ:
1. 人によるレビューで詳細な確認
2. プロジェクト固有の要件や基準に基づく評価
3. 必要に応じたテストコードの手動修正
4. レビュー結果に基づく、テストコード生成プロセスの改善検討


## テストコード作成手順ルール:
テストシナリオの設計:
- [メソッド名]の機能を分析し、C0（命令網羅）、C1（分岐網羅）、C2（条件網羅）の観点でテストシナリオを考えてください。
- 考えたテストシナリオをMindmap形式で表現し、C0、C1、C2の区分を明示してください。

## テストクラスの作成ルール:
- Test_[クラス名]_[メソッド名]という名前のテストクラスを作成してください。
- クラスのdocstringに、作成したC0、C1、C2区分を明示したMindmap outlineを全て記載し全体見通しを明確にしてください。

## テストメソッドの実装ルール:
- test_test_[メソッド名]_[テストカテゴリ]_[テストシナリオ概要]でメソッドをテストする関数を作成してください
  - テスト区分； ut or it
  - テストカテゴリ； C0 or C1 or C2
- C0、C1、C2の各カテゴリに対応するテストメソッドを実装してください。
- 各テストメソッドには以下の情報を含むdocstringをtest_docという変数格納するよう記述してください：
  - テスト区分（正常系 or 異常系/UT or IT）
  - テストカテゴリ（C0 or C1 or C2）
  - テストシナリオの説明
- テストメソッド内では、適切なアサーションを使用して期待される動作を検証してください
- サンプルコードと同様のコメントを付与してください
- 他のテストカテゴリーテストでカバー済のものはその旨を記載してください

## ログ出力ルール:
- 各テストメソッドの冒頭で、テスト関数名を含むログメッセージを出力してください。
- テストの重要なステップでログメッセージを出力し、テストの流れを追跡可能にしてください。

## 例外処理とエッジケースルール:
- 必要に応じて、例外が発生するケースのテストを含めてください。
- エッジケース（境界値、特殊な入力など）についても考慮し、テストを作成してください。

## コードスタイルルール:
- PEP8に準拠したコードスタイルを使用してください。
- 適切な変数名とコメントを使用し、コードの可読性を高めてください。

## 注意事項:
- 実際の環境で再現が難しいテストケース（例：メモリ不足）については、コメントアウトし、その理由を説明してください。
- テストコードは、提供されたサンプルコードの形式と構造に厳密に準拠してください。特に、クラスのdocstring、テストメソッドの命名規則、ログ出力の形式などに注意してください。
- このプロンプトとサンプルコードに従ってテストコードを作成してください。サンプルコードの構造と形式を模倣することが重要です。不明な点がある場合は、質問してください。

## ディシジョンテーブルフォーマット
以下の構成Matrixを作成してください,４つの象限で構成されます。

1.条件記述部
考慮すべき条件を列挙して記述する部分です。条件を記述するので条件記述部と呼ばれます。

2.動作記述部
考慮すべき動作（出力結果）を列挙して記述する部分です。動作を記述するので動作記述部と呼ばれます。

3.条件指定部
1.の条件記述を満たすかどうか、つまり真か偽かをYかNで表します。\YはYesの頭文字であり、他にもT（True）と表現する場合もあります。NはNoの頭文字であり、他にもF（False）と表現する場合もあります。各条件記述のY/Nの組み合わせを指定するので、条件指定部と呼ばれます。

4.動作指定部
各列（これを"規則"と呼びます）で指定されている条件指定のY/Nの組み合わせによって決まる出力結果（動作）を示します。その条件の組み合わせによって動作する動作記述に「X」を指定します。バツではなくeXecution（実行）を意味します。「－」は逆に動作しないことを示します。動作を指定するので、動作指定部と呼びます。

## テスト定義、テスト開始、テスト終了メッセージのログ出力
サンプルコードにある
- test_doc定義のlog_msg出力
- テスト開始log_msg出力
- テスト終了log_msg出力
を適切なタイミングで必ず行ってください


## python バージョン
3.11.6以降を使用します、古い書き方は採用しません

## 確認
前提・要件はOKでしょうか

いちどここで立ち止まりましょう

## では<step0>から進めましょう

### サンプルコード:
```python
import pytest
from pathlib import Path

####################################
# テスト対象モジュールimport
####################################
from src.lib.convertor_utils.ibr_excel_field_analyzer import RemarksParser

####################################
# テストサポートモジュールimport
####################################
from src.lib.common_utils.ibr_enums import LogLevel
from src.lib.common_utils.ibr_get_config import Config

package_path = Path(__file__)
config = Config.load(package_path)

log_msg = config.log_message
log_msg(str(config), LogLevel.DEBUG)

class TestBusinessUnitCodeConverterInit:
    """BusinessUnitCodeConverterの__init__メソッドのテスト

    テスト構造:
    ├── C0: 基本機能テスト
    │   ├── 正常系: 有効な変換テーブルファイルでインスタンス生成
    │   ├── 異常系: 存在しないファイルでFileNotFoundError
    │   └── 異常系: 無効なファイル形式でException
    ├── C1: 分岐カバレッジ
    │   ├── 正常系: try文が正常に実行される
    │   ├── 異常系: FileNotFoundError分岐
    │   ├── 異常系: 無効なファイル形式でその他のException分岐
    │   └── 異常系: 権限エラーでその他のException分岐
    └── C2: 条件組み合わせ
        ├── 正常系: 有効なファイルでインスタンスが正常に生成される
        ├── 異常系: 存在しないファイルでFileNotFoundError
        ├── 異常系: 無効なpickleファイルでException
        ├── 異常系: 空のDataFrameを含むpickleファイルでException
        └── 異常系: 無効な構造のDataFrameを含むpickleファイルでException

    # C1のディシジョンテーブル
    | 条件                          | ケース1                | ケース2           | ケース3                    | ケース4                |
    |-------------------------------|------------------------|-------------------|----------------------------|------------------------|
    | ファイルが存在する            | Y                      | N                 | Y                          | Y                      |
    | ファイルが有効なpickle形式    | Y                      | -                 | N                          | Y                      |
    | ファイルに読み取り権限がある  | Y                      | -                 | -                          | N                      |
    | 出力                          | 正常にインスタンス生成 | FileNotFoundError | Exception (無効なファイル) | Exception (権限エラー) |
    """
    def setup_method(self):
        # テスト定義をログ出力 このまま記述してください
        log_msg("test start", LogLevel.INFO)

    def teardown_method(self):
        log_msg(f"test end\n{'-'*80}\n", LogLevel.INFO)

    @pytest.fixture()
    def valid_conversion_table(self, tmp_path):
        """有効な変換テーブルのfixture"""
        file_path = tmp_path / "valid_table.pkl"
        df = pd.DataFrame({
            'business_unit_code_jinji': ['001', '002'],
            'main_business_unit_code_jinji': ['M001', 'M002'],
            'business_unit_code_bpr': ['B001', 'B002']
        })
        with file_path.open('wb') as f:
            pickle.dump(df, f)
        return file_path

    def test_init_C0_valid_file(self, valid_conversion_table):
        test_doc = """テスト内容:

        - テストカテゴリ: C0
        - テスト区分: 正常系
        - テストシナリオ: 有効な変換テーブルファイルでインスタンス生成
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)
 
        converter = BusinessUnitCodeConverter(valid_conversion_table)
        assert isinstance(converter.conversion_table, pd.DataFrame)
        assert not converter.conversion_table.empty


    def test_init_C0_file_not_found(self, tmp_path):
        test_doc = """テスト内容:

        - テストカテゴリ: C0
        - テスト区分: 異常系
        - テストシナリオ: 存在しないファイルでFileNotFoundError
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        non_existent_file = tmp_path / "non_existent.pkl"
        with pytest.raises(FileNotFoundError):
            BusinessUnitCodeConverter(non_existent_file)


    @pytest.mark.parametrize(("file_name", "expected"), [
        ("人事_申請データ.xlsx", 1),
        ("国企_申請データ.xlsx", 2),
        ("関連(ダミー課あり)_申請データ.xlsx", 3),
        ("関連(ダミー課なし)_申請データ.xlsx", 4),
    ])
    def test_generate_applicant_info_C0_valid_input(self, file_name, expected):
        test_doc = """テスト内容:
        - テストカテゴリ: C0
        - テスト区分: 正常系
        - テストシナリオ: 有効な入力でのテスト
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        result = generate_applicant_info(file_name)
        assert result == expected
        log_msg(f"Result: {result}", LogLevel.DEBUG)

    def test_generate_applicant_info_C2_case_and_bracket(self, file_name, expected):
        test_doc = """テスト内容:
        - テストカテゴリ: C2
        - テスト区分: 正常系
        - テストシナリオ: 大文字小文字と括弧の組み合わせテスト
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        applicant_types = {
            "人事": 1,
            "国企": 2,
            "関連(ダミー課あり)": 3,
            "関連(ダミー課なし)": 4,
        }

        if not any(key in file_name.lower() for key in applicant_types):
            with pytest.raises(ValueError) as exc_info:
                generate_applicant_info(file_name)
            error_message = str(exc_info.value)
            log_msg(f"ValueError raised: {error_message}", LogLevel.ERROR)
            assert "不正なファイル名パターン" in error_message
        else:
            result = generate_applicant_info(file_name)
            assert result == expected
            log_msg(f"Result: {result}", LogLevel.DEBUG)
```
いちどここで立ち止まりましょう



## それではStep1に進みます

## テスト対象モジュール配置場所
src.lib.converter_utils

## テスト対象モジュール名
ibr_reference_merger.py

## テスト対象モジュール
"""一括申請明細にリファレンステーブル情報をマージして情報付与する"""
import pandas as pd
from typing import  Any
from src.lib.common_utils.ibr_pickled_table_searcher import TableSearcher

class ReferenceMerger:
    """統合レイアウトデータとリファレンステーブルのマージを行うクラス

    Class Overview:
        このクラスはデータ取り込み後の統合レイアウトデータと
        リファレンステーブルの情報をマージする機能を提供します。
        部店コードの上位4桁を使用してリファレンステーブルを検索し、
        条件に合致する一部のColumnデータを統合レイアウトにマージします。

    Attributes:
        table_searcher (TableSearcher): リファレンステーブルの検索を行うオブジェクト

    Condition Information:
        - Condition:1
            - ID: ZERO_SECTION_GR_CODE
            - Type: フィルタリング条件
            - Applicable Scenarios: リファレンステーブルから課グループコードが'0'のレコードを選択する

    Pattern Information:
        - Pattern:1
            - ID: BRANCH_CODE_PREFIX_MATCH
            - Type: 検索パターン
            - Applicable Scenarios: 部店コードの上位4桁を使用してリファレンステーブルを検索する

    Methods:
        merge_reference_data(integrated_layout: pd.DataFrame) -> pd.DataFrame:
            統合レイアウトデータにリファレンス情報をマージする
        _get_reference_info(row: pd.Series) -> dict[str, Any]:
            1行のデータに対応するリファレンス情報を取得する
        _get_branch_code_prefix(row: pd.Series) -> str:
            部店コードの上位4桁を取得する
        _search_reference_table(branch_code_prefix: str) -> pd.DataFrame:
            リファレンステーブルを検索する
        _filter_zero_row(df: pd.DataFrame) -> pd.DataFrame:
            課グループコードが'0'の行をフィルタリングする
        _create_result_dict(row: pd.Series) -> dict[str, Any]:
            リファレンス情報の辞書を作成する
        _get_empty_result() -> dict[str, Any]:
            空のリファレンス情報辞書を返す

    Usage Example:
        >>> from src.lib.common_utils.ibr_pickled_table_searcher import TableSearcher
        >>> from src.lib.converter_utils.ibr_reference_merger import ReferenceMerger
        >>> table_searcher = TableSearcher("reference_table.pkl")
        >>> merger = ReferenceMerger(table_searcher)
        >>> integrated_layout = pd.read_csv("integrated_layout.csv")
        >>> merged_data = merger.merge_reference_data(integrated_layout)
        >>> print(merged_data.head())

    Notes:
        - リファレンステーブルは事前にpickleファイルとして保存されている必要があります
        - 大量のデータを処理する場合、メモリ使用量に注意してください

    Dependency:
        - pandas
        - src.lib.common_utils.ibr_pickled_table_searcher.TableSearcher

    ResourceLocation:
        - [本体]
            - src/lib/converter_utils/ibr_reference_merger.py
        - [テストコード]
            - tests/lib/converter_utils/test_ibr_reference_merger.py

    Todo:
        - パフォーマンスの最適化
        - 並列処理の導入検討
        - エラーハンドリングの強化

    Change History:
    | No   | 修正理由     | 修正点   | 対応日     | 担当         |
    |------|--------------|----------|------------|--------------|
    | v0.1 | 初期定義作成 | 新規作成 | 2024/08/18 | xxxx aaa.bbb |

    """

    def __init__(self, table_searcher: TableSearcher):
        """コンストラクタ

        Arguments:
        table_searcher (TableSearcher): リファレンステーブルの検索を行うオブジェクト
        """
        self.table_searcher = table_searcher

    def merge_reference_data(self, integrated_layout: pd.DataFrame) -> pd.DataFrame:
        """統合レイアウトデータにリファレンステーブルの情報をマージする

        Arguments:
        integrated_layout (pd.DataFrame): 統合レイアウトデータ

        Return Value:
        pd.DataFrame: マージされたデータフレーム

        Algorithm:
            1. 統合レイアウトの各行に対して_get_reference_infoメソッドを適用
            2. 得られた結果を元のDataFrameとマージして返す

        Exception:
        ValueError: 入力DataFrameが空の場合

        Usage Example:
        >>> merged_data = merger.merge_reference_data(integrated_layout)
        >>> print(merged_data.columns)
        Index(['branch_code', 'other_data', 'reference_branch_code', 'reference_branch_name', 'reference_parent_branch_code'], dtype='object')
        """
        if integrated_layout.empty:
            err_msg = "入力DataFrameが空です"
            raise ValueError(err_msg) from None

        reference_info = integrated_layout.apply(self._get_reference_info, axis=1, result_type='expand')
        return pd.concat([integrated_layout, reference_info], axis=1)

    def _get_reference_info(self, row: pd.Series) -> dict[str, Any]:
        """1行のデータに対応するリファレンス情報を取得する

        Arguments:
        row (pd.Series): 統合レイアウトの1行のデータ

        Return Value:
        dict[str, Any]: 取得したリファレンス情報

        Algorithm:
            1. 部店コードの上位4桁を取得
            2. リファレンステーブルを検索
            3. 検索結果から条件に合う行を抽出
            4. 結果の辞書を作成して返す

        Exception:
        KeyError: 必要なカラムが存在しない場合
        """
        try:
            branch_code_prefix = self._get_branch_code_prefix(row)
            matching_rows = self._search_reference_table(branch_code_prefix)
            zero_row = self._filter_zero_row(matching_rows)

            if zero_row.empty:
                return self._get_empty_result()
            return self._create_result_dict(zero_row.iloc[0])
        except KeyError:
            #必要なカラムが存在しない
            return self._get_empty_result()

    def _get_branch_code_prefix(self, row: pd.Series) -> str:
        """部店コードの上位4桁を取得する"""
        return str(row['branch_code'])[:4]

    def _search_reference_table(self, branch_code_prefix: str) -> pd.DataFrame:
        """リファレンステーブルを検索する"""
        return self.table_searcher.simple_search({
            "branch_code_bpr": f"startswith:{branch_code_prefix}",
        })

    def _filter_zero_row(self, df: pd.DataFrame) -> pd.DataFrame:
        """課グループコードが'0'の行をフィルタリングする"""
        return df[df['section_gr_code_bpr'] == '0']

    def _create_result_dict(self, row: pd.Series) -> dict[str, Any]:
        """リファレンス情報の辞書を作成する"""
        return {
            "reference_branch_code": row['branch_code_bpr'],
            "reference_branch_name": row['branch_name_bpr'],
            "reference_parent_branch_code": row['parent_branch_code'] if pd.notna(row['parent_branch_code']) else None,
        }

    def _get_empty_result(self) -> dict[str, Any]:
        """空のリファレンス情報辞書を返す"""
        return {
            "reference_branch_code": None,
            "reference_branch_name": None,
            "reference_parent_branch_code": None,
        }




---

いちどここで立ち止まりましょう

## 続いてstepxを実施していきます

以後、stepの過程で詰めたり確認したりさまざまやりつつ前に進めます




