"""テスト実施方法

# project topディレクトリから実行する
$ pwd
/developer/library_dev/project_1

# pytest結果をファイル出力する場合
$ pytest -lv ./tests/lib/common_utils/test_ibr_csv_helper.py > tests/log/pytest_result.log

# pytest結果を標準出力する場合
$ pytest -lv ./tests/lib/common_utils/test_ibr_csv_helper.py
"""
import sys
from pathlib import Path
from unittest.mock import MagicMock

import pandas as pd
import pytest

from src.lib.common_utils.ibr_decorator_config import initialize_config
from src.lib.common_utils.ibr_enums import LogLevel
from src.lib.converter_utils.ibr_excel_field_analyzer import (
    RemarksParser,
)

config = initialize_config(sys.modules[__name__])
log_msg = config.log_message
log_msg(str(config), LogLevel.DEBUG)

#class Test_RemarksParser:
#    """RemarksParser Classのテスト全体をまとめたClass
#
#    RemarksParser.parse()
#    │
#    ├─ C0(命令網羅)
#    │   └─ 基本的な解析処理
#    │       ├─ 営業部署情報の解析
#    │       ├─ エリアグループ情報の解析
#    │       └─ その他の情報の解析
#    │
#    ├─ C1(分岐網羅)
#    │   ├─ 営業部署情報の分岐
#    │   │   ├─ 通常の営業部
#    │   │   └─ 数字付きの営業部
#    │   ├─ エリアグループ情報の分岐
#    │   │   ├─ 設立日あり
#    │   │   └─ 設立日なし
#    │   └─ その他の情報の分岐
#    │       └─ 変更、廃止を含む情報
#    │
#    └─ C2(条件網羅)
#        ├─ 入力テキストの種類
#        │   ├─ 営業部署情報のみ
#        │   ├─ エリアグループ情報のみ
#        │   └─ その他の情報のみ
#        └─ 特殊なケース
#            ├─ 空の入力
#            └─ 複数行の入力
#    """
#    def setup_method(self):
#        log_msg("test start", LogLevel.INFO)
#
#    def teardown_method(self):
#        log_msg(f"test end\n{'-'*80}\n", LogLevel.INFO)
#
#    @pytest.mark.parametrize(
#        ("remarks_text", "expected_result"),
#        [
#            (
#                "八重洲通支店営業部",
#                {
#                    "request_type": "営業部傘下",
#                    "sales_department": {
#                        #"department_name": "八重洲通支店営業部",
#                        "department_name": "営業部",
#                        "branch_name": "八重洲通支店",
#                    },
#                    "area_group": {
#                        "group_code": "",
#                        "group_name": "",
#                        "established_date": "",
#                    },
#                    "other_info": "",
#                },
#            ),
#            (
#                "笹島支店営業第一部",
#                {
#                    "request_type": "営業部傘下",
#                    "sales_department": {
#                        #"department_name": "笹島支店第一営業部",
#                        "department_name": "営業第一部",
#                        "branch_name": "笹島支店",
#                    },
#                    "area_group": {
#                        "group_code": "",
#                        "group_name": "",
#                        "established_date": "",
#                    },
#                    "other_info": "",
#                },
#            ),
#
#            # ケース1: シンプルな営業部 ○○営業部△△営業部
#            (
#                "大阪営業部営業部",
#                {
#                    "request_type": "営業部傘下",
#                    "sales_department": {
#                        "department_name": "営業部",
#                        "branch_name": "大阪営業部",
#                    },
#                    "area_group": {
#                        "group_code": "",
#                        "group_name": "",
#                        "established_date": "",
#                    },
#                    "other_info": "",
#                },
#            ),
#            # ケース1: シンプルな営業部 ○○営業部△△営業部
#            (
#                "大阪営業部岸和田営業部",
#                {
#                    "request_type": "営業部傘下",
#                    "sales_department": {
#                        "department_name": "岸和田営業部",
#                        "branch_name": "大阪営業部",
#                    },
#                    "area_group": {
#                        "group_code": "",
#                        "group_name": "",
#                        "established_date": "",
#                    },
#                    "other_info": "",
#                },
#            ),
#
#            # ケース2: 営業第X部
#            (
#                "東京営業部営業第一部",
#                {
#                    "request_type": "営業部傘下",
#                    "sales_department": {
#                        "department_name": "営業第一部",
#                        "branch_name": "東京営業部",
#                    },
#                    "area_group": {
#                        "group_code": "",
#                        "group_name": "",
#                        "established_date": "",
#                    },
#                    "other_info": "",
#                },
#            ),
#
#            # 要件としては発生しない前提
#            ## ケース4: 中間に営業部があるケース
#            #(
#            #    "大阪営業部営業部営業部",
#            #    {
#            #        "request_type": "営業部傘下",
#            #        "sales_department": {
#            #            "department_name": "営業部",
#            #            "branch_name": "大阪営業部",
#            #        },
#            #        "area_group": {
#            #            "group_code": "",
#            #            "group_name": "",
#            #            "established_date": "",
#            #        },
#            #        "other_info": "",
#            #    },
#            #),
#
#            # 要件としては発生しない前提
#            ## ケース5: 中間に営業部があり、末尾が営業第X部
#            #(
#            #    "大阪営業部営業部営業第二部",
#            #    {
#            #        "request_type": "営業部傘下",
#            #        "sales_department": {
#            #            "department_name": "営業第二部",
#            #            "branch_name": "大阪営業部",
#            #        },
#            #        "area_group": {
#            #            "group_code": "",
#            #            "group_name": "",
#            #            "established_date": "",
#            #        },
#            #        "other_info": "",
#            #    },
#            #),
#
#            (
#                "41002 東日本第一Gr",
#                {
#                    "request_type": "エリア",
#                    "sales_department": {
#                        "department_name": "",
#                        "branch_name": "",
#                    },
#                    "area_group": {
#                        "group_code": "41002",
#                        "group_name": "東日本第一Gr",
#                        "established_date": "",
#                    },
#                    "other_info": "",
#                },
#            ),
#            (
#                "41012　グローバル財務戦略Gr (4/1新設)",
#                {
#                    "request_type": "エリア",
#                    "sales_department": {
#                        "department_name": "",
#                        "branch_name": "",
#                    },
#                    "area_group": {
#                        "group_code": "41012",
#                        "group_name": "グローバル財務戦略Gr",
#                        "established_date": "4/1新設",
#                    },
#                    "other_info": "",
#                },
#            ),
#            (
#                "C1:法人・リテール部門、C1:法人・リテール部門より変更",
#                {
#                    "request_type": "その他",
#                    "sales_department": {
#                        "department_name": "",
#                        "branch_name": "",
#                    },
#                    "area_group": {
#                        "group_code": "",
#                        "group_name": "",
#                        "established_date": "",
#                    },
#                    "other_info": "C1:法人・リテール部門、C1:法人・リテール部門より変更",
#                },
#            ),
#            (
#                "2022.12.11廃止済みの課復活",
#                {
#                    "request_type": "その他",
#                    "sales_department": {
#                        "department_name": "",
#                        "branch_name": "",
#                    },
#                    "area_group": {
#                        "group_code": "",
#                        "group_name": "",
#                        "established_date": "",
#                    },
#                    "other_info": "2022.12.11廃止済みの課復活",
#                },
#            ),
#        ],
#    )
#    def test_parse_UT_C0_normal_case(self, remarks_text, expected_result):
#        test_doc = """テスト定義:
#
#        - テストカテゴリ: C0
#        - テスト区分: 正常系/UT
#        - テストシナリオ: RemarksParserの基本的な解析処理の確認
#        """
#        log_msg(f"\n{test_doc}", LogLevel.DEBUG)
#
#        # インスタンス生成
#        parser = RemarksParser()
#
#        # 結果定義,関数実行
#        result = parser.parse(remarks_text)
#
#        log_msg(f'Input text: {remarks_text}', LogLevel.DEBUG)
#        log_msg(f'Expected result: {expected_result}', LogLevel.DEBUG)
#        log_msg(f'Actual result: {result}', LogLevel.DEBUG)
#
#        # 結果評価
#        assert result == expected_result, f"Expected {expected_result}, but got {result}"


class Test_RemarksParser_init:
    """RemarksParserの__init__メソッドのテスト

    テスト構造:
    ├── C0: 基本機能テスト
    │   └── 初期化の正常系テスト
    │       ├── result辞書の初期構造確認
    │       └── 各フィールドの初期値確認
    │
    ├── C1: 分岐カバレッジ
    │   └── (分岐なし)
    │
    ├── C2: 条件組み合わせ
    │   ├── result辞書の型チェック
    │   └── 内部辞書の型と構造チェック
    │
    └── BVT: 境界値テスト
        └── メモリ制約での初期化

    ディシジョンテーブル:
    | No | 条件                                | Case1 | Case2 | Case3 | Case4 |
    |----|-------------------------------------|-------|-------|-------|-------|
    | 1  | resultがdict型である                | Y     | Y     | Y     | Y     |
    | 2  | request_typeが空文字列である        | Y     | N     | Y     | Y     |
    | 3  | sales_departmentが正しい構造である  | Y     | Y     | N     | Y     |
    | 4  | area_groupが正しい構造である        | Y     | Y     | Y     | N     |
    | 出力| 初期化成功                         | Y     | N     | N     | N     |

    境界値検証ケース一覧:
    | ID     | パラメータ | テスト値              | 期待される結果 | テストの目的            | 実装状況                             |
    |--------|------------|-----------------------|----------------|-------------------------|--------------------------------------|
    | BVT_001| なし       | 通常の初期化          | 成功           | 基本動作の確認          | test_init_C0_basic_instance_creation |
    | BVT_002| なし       | メモリ制約下での初期化| MemoryError    | リソース制限時の動作確認| test_init_BVT_memory_constraint      |
    """

    def setup_method(self):
        """テストメソッドの実行前処理"""
        log_msg("test start", LogLevel.INFO)

    def teardown_method(self):
        """テストメソッドの実行後処理"""
        log_msg(f"test end\n{'-'*80}\n", LogLevel.INFO)

    def test_init_C0_basic_instance_creation(self):
        """テスト区分: UT

        テストカテゴリ: C0
        テストシナリオ: 基本的なインスタンス生成と結果辞書の初期化確認
        """
        test_doc = """テスト定義:
        - テストカテゴリ: C0
        - テスト区分: 正常系/UT
        - テストシナリオ: 基本的なインスタンス生成と結果辞書の初期化確認
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        parser = RemarksParser()
        log_msg(f'Result dictionary: {parser.result}', LogLevel.DEBUG)

        assert isinstance(parser.result, dict)
        assert parser.result["request_type"] == ""
        assert "sales_department" in parser.result
        assert "area_group" in parser.result
        assert parser.result["other_info"] == ""

    def test_init_C2_dictionary_structure(self):
        """テスト区分: UT

        テストカテゴリ: C2
        テストシナリオ: 内部辞書の型と構造の詳細チェック
        """
        test_doc = """テスト定義:
        - テストカテゴリ: C2
        - テスト区分: 正常系/UT
        - テストシナリオ: 内部辞書の型と構造の詳細チェック
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        parser = RemarksParser()
        log_msg(f'Result dictionary structure: {parser.result}', LogLevel.DEBUG)

        # result辞書の構造チェック
        assert isinstance(parser.result["sales_department"], dict)
        assert isinstance(parser.result["area_group"], dict)
        assert isinstance(parser.result["other_info"], str)

        # sales_department辞書の構造チェック
        assert "department_name" in parser.result["sales_department"]
        assert "branch_name" in parser.result["sales_department"]
        assert parser.result["sales_department"]["department_name"] == ""
        assert parser.result["sales_department"]["branch_name"] == ""

        # area_group辞書の構造チェック
        assert "group_code" in parser.result["area_group"]
        assert "group_name" in parser.result["area_group"]
        assert "established_date" in parser.result["area_group"]
        assert parser.result["area_group"]["group_code"] == ""
        assert parser.result["area_group"]["group_name"] == ""
        assert parser.result["area_group"]["established_date"] == ""

    @pytest.mark.skip(reason="実環境でのメモリ制約テストは実施不可")
    def test_init_BVT_memory_constraint(self, monkeypatch):
        """テスト区分: UT

        テストカテゴリ: BVT
        テストシナリオ: メモリ制約下でのインスタンス生成
        """
        test_doc = """テスト定義:
        - テストカテゴリ: BVT
        - テスト区分: 異常系/UT
        - テストシナリオ: メモリ制約下でのインスタンス生成テスト
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        def mock_dict(*args, **kwargs):
            err_msg = "Simulated memory constraint"
            raise MemoryError(err_msg) from None

        monkeypatch.setattr("builtins.dict", mock_dict)

        with pytest.raises(MemoryError) as exc_info:
            RemarksParser()

        assert "Simulated memory constraint" in str(exc_info.value)

class Test_RemarksParser_parse:
    r"""RemarksParserのparseメソッドのテスト

    テスト構造:
    ├── C0: 基本機能テスト
    │   ├── 営業部署情報の基本パターン
    │   ├── エリアグループ情報の基本パターン
    │   └── その他情報の基本パターン
    │
    ├── C1: 分岐カバレッジ
    │   ├── request_typeの分岐
    │   │   ├── 営業部傘下パターン
    │   │   ├── エリアパターン
    │   │   └── その他パターン
    │   └── キーワード判定の分岐
    │       └── 変更/廃止/共通認証の含有判定
    │
    ├── C2: 条件組み合わせ
    │   ├── 入力タイプの組み合わせ
    │   │   ├── 単一タイプ入力
    │   │   └── 複数タイプの混在
    │   └── 特殊パターン
    │       ├── 空入力
    │       └── 不正フォーマット
    │
    ├── DT: ディシジョンテーブル
    │   ├── 営業部署パターン組み合わせ
    │   └── エリアグループパターン組み合わせ
    │
    └── BVT: 境界値テスト
        ├── 文字列長
        ├── 特殊文字
        └── 空白文字バリエーション

    ディシジョンテーブル:
    | No | 条件                           | Case1 | Case2 | Case3 | Case4 | Case5 | Case6 |
    |----|--------------------------------|-------|-------|-------|-------|-------|-------|
    | 1  | 営業部署情報を含む             | Y     | N     | N     | Y     | N     | N     |
    | 2  | エリアグループ情報を含む       | N     | Y     | N     | Y     | N     | N     |
    | 3  | 変更/廃止/共通認証を含む       | N     | N     | Y     | N     | N     | N     |
    | 4  | 入力が空または不正             | N     | N     | N     | N     | Y     | Y     |
    | 5  | 複数行入力                     | N     | N     | N     | Y     | N     | N     |
    |出力| request_type                   | 営業  | エリア| その他| 混在  | その他| エラー|

    境界値検証ケース一覧:
    | ID     | パラメータ    | テスト値                 | 期待される結果 | テストの目的        | 実装状況                       |
    |--------|---------------|--------------------------|----------------|---------------------|--------------------------------|
    | BVT_001| remarks_text  | ""                       | その他         | 空文字列の処理      | test_parse_BVT_empty_input     |
    | BVT_002| remarks_text  | None                     | TypeError      | None入力の処理      | test_parse_BVT_none_input      |
    | BVT_003| remarks_text  | "A" * 1000               | 正常処理       | 長い文字列の処理    | test_parse_BVT_long_input      |
    | BVT_004| remarks_text  | "特殊文字@#$%"           | その他         | 特殊文字の処理      | test_parse_BVT_special_chars   |
    | BVT_005| remarks_text  | "\n\n\n"                 | その他         | 空白行のみの処理    | test_parse_BVT_only_whitespace |
    """

    def setup_method(self):
        """テストメソッドの実行前処理"""
        log_msg("test start", LogLevel.INFO)
        self.parser = RemarksParser()

    def teardown_method(self):
        """テストメソッドの実行後処理"""
        log_msg(f"test end\n{'-'*80}\n", LogLevel.INFO)

    @pytest.mark.parametrize(("remarks_text", "expected"), [
        (
            "八重洲通支店営業部",
            {
                "request_type": "営業部傘下",
                "sales_department": {
                    "department_name": "営業部",
                    "branch_name": "八重洲通支店",
                },
                "area_group": {
                    "group_code": "",
                    "group_name": "",
                    "established_date": "",
                },
                "other_info": "",
            },
        ),
        (
            "41002 東日本第一Gr",
            {
                "request_type": "エリア",
                "sales_department": {
                    "department_name": "",
                    "branch_name": "",
                },
                "area_group": {
                    "group_code": "41002",
                    "group_name": "東日本第一Gr",
                    "established_date": "",
                },
                "other_info": "",
            },
        ),
    ])
    def test_parse_C0_basic_patterns(self, remarks_text, expected):
        """テスト区分: UT

        テストカテゴリ: C0
        テストシナリオ: 基本的な入力パターンの処理確認
        """
        test_doc = """テスト定義:
        - テストカテゴリ: C0
        - テスト区分: 正常系/UT
        - テストシナリオ: 基本的な入力パターンのテスト
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)
        log_msg(f"Input text: {remarks_text}", LogLevel.DEBUG)

        result = self.parser.parse(remarks_text)
        log_msg(f"Result: {result}", LogLevel.DEBUG)

        assert result == expected

    @pytest.mark.parametrize(("remarks_text", "expected_type"), [
        ("八重洲通支店営業部", "営業部傘下"),
        ("41002 東日本第一Gr", "エリア"),
        ("変更申請", "その他"),
        ("廃止予定", "その他"),
        ("共通認証対応", "その他"),
    ])
    def test_parse_C1_request_type_branches(self, remarks_text, expected_type):
        """テスト区分: UT

        テストカテゴリ: C1
        テストシナリオ: request_typeの分岐処理確認
        """
        test_doc = """テスト定義:
        - テストカテゴリ: C1
        - テスト区分: 正常系/UT
        - テストシナリオ: request_type分岐のテスト
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)
        log_msg(f"Input text: {remarks_text}", LogLevel.DEBUG)

        result = self.parser.parse(remarks_text)
        log_msg(f"Result type: {result['request_type']}", LogLevel.DEBUG)

        assert result["request_type"] == expected_type

    @pytest.mark.parametrize(("remarks_text", "expected_result"), [
        (
            "八重洲通支店営業部\n41002 東日本第一Gr",
            {
                "request_type": "営業部傘下",
                "sales_department": {
                    "department_name": "営業部",
                    "branch_name": "八重洲通支店",
                },
                "area_group": {
                    "group_code": "",
                    "group_name": "",
                    "established_date": "",
                },
                "other_info": "41002 東日本第一Gr",
            },
        ),
            (
                "八重洲通支店営業部",
                {
                    "request_type": "営業部傘下",
                    "sales_department": {
                        #"department_name": "八重洲通支店営業部",
                        "department_name": "営業部",
                        "branch_name": "八重洲通支店",
                    },
                    "area_group": {
                        "group_code": "",
                        "group_name": "",
                        "established_date": "",
                    },
                    "other_info": "",
                },
            ),
            (
                "笹島支店営業第一部",
                {
                    "request_type": "営業部傘下",
                    "sales_department": {
                        #"department_name": "笹島支店第一営業部",
                        "department_name": "営業第一部",
                        "branch_name": "笹島支店",
                    },
                    "area_group": {
                        "group_code": "",
                        "group_name": "",
                        "established_date": "",
                    },
                    "other_info": "",
                },
            ),

            # ケース1: シンプルな営業部 ○○営業部△△営業部
            (
                "大阪営業部営業部",
                {
                    "request_type": "営業部傘下",
                    "sales_department": {
                        "department_name": "営業部",
                        "branch_name": "大阪営業部",
                    },
                    "area_group": {
                        "group_code": "",
                        "group_name": "",
                        "established_date": "",
                    },
                    "other_info": "",
                },
            ),
            # ケース1: シンプルな営業部 ○○営業部△△営業部
            (
                "大阪営業部岸和田営業部",
                {
                    "request_type": "営業部傘下",
                    "sales_department": {
                        "department_name": "岸和田営業部",
                        "branch_name": "大阪営業部",
                    },
                    "area_group": {
                        "group_code": "",
                        "group_name": "",
                        "established_date": "",
                    },
                    "other_info": "",
                },
            ),

            # ケース2: 営業第X部
            (
                "東京営業部営業第一部",
                {
                    "request_type": "営業部傘下",
                    "sales_department": {
                        "department_name": "営業第一部",
                        "branch_name": "東京営業部",
                    },
                    "area_group": {
                        "group_code": "",
                        "group_name": "",
                        "established_date": "",
                    },
                    "other_info": "",
                },
            ),

            # 要件としては発生しない前提
            ## ケース4: 中間に営業部があるケース
            #(
            #    "大阪営業部営業部営業部",
            #    {
            #        "request_type": "営業部傘下",
            #        "sales_department": {
            #            "department_name": "営業部",
            #            "branch_name": "大阪営業部",
            #        },
            #        "area_group": {
            #            "group_code": "",
            #            "group_name": "",
            #            "established_date": "",
            #        },
            #        "other_info": "",
            #    },
            #),

            # 要件としては発生しない前提
            ## ケース5: 中間に営業部があり、末尾が営業第X部
            #(
            #    "大阪営業部営業部営業第二部",
            #    {
            #        "request_type": "営業部傘下",
            #        "sales_department": {
            #            "department_name": "営業第二部",
            #            "branch_name": "大阪営業部",
            #        },
            #        "area_group": {
            #            "group_code": "",
            #            "group_name": "",
            #            "established_date": "",
            #        },
            #        "other_info": "",
            #    },
            #),

            (
                "41002 東日本第一Gr",
                {
                    "request_type": "エリア",
                    "sales_department": {
                        "department_name": "",
                        "branch_name": "",
                    },
                    "area_group": {
                        "group_code": "41002",
                        "group_name": "東日本第一Gr",
                        "established_date": "",
                    },
                    "other_info": "",
                },
            ),
            (
                "41012　グローバル財務戦略Gr (4/1新設)",
                {
                    "request_type": "エリア",
                    "sales_department": {
                        "department_name": "",
                        "branch_name": "",
                    },
                    "area_group": {
                        "group_code": "41012",
                        "group_name": "グローバル財務戦略Gr",
                        "established_date": "4/1新設",
                    },
                    "other_info": "",
                },
            ),
            (
                "C1:法人・リテール部門、C1:法人・リテール部門より変更",
                {
                    "request_type": "その他",
                    "sales_department": {
                        "department_name": "",
                        "branch_name": "",
                    },
                    "area_group": {
                        "group_code": "",
                        "group_name": "",
                        "established_date": "",
                    },
                    "other_info": "C1:法人・リテール部門、C1:法人・リテール部門より変更",
                },
            ),
            (
                "2022.12.11廃止済みの課復活",
                {
                    "request_type": "その他",
                    "sales_department": {
                        "department_name": "",
                        "branch_name": "",
                    },
                    "area_group": {
                        "group_code": "",
                        "group_name": "",
                        "established_date": "",
                    },
                    "other_info": "2022.12.11廃止済みの課復活",
                },
            ),
    ])
    def test_parse_C2_combined_inputs(self, remarks_text, expected_result):
        """テスト区分: UT

        テストカテゴリ: C2
        テストシナリオ: 複数タイプの入力の組み合わせテスト
        """
        test_doc = """テスト定義:
        - テストカテゴリ: C2
        - テスト区分: 正常系/UT
        - テストシナリオ: 複数タイプ入力の組み合わせテスト
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)
        log_msg(f"Input text:\n{remarks_text}", LogLevel.DEBUG)

        result = self.parser.parse(remarks_text)
        log_msg(f"Result: {result}", LogLevel.DEBUG)

        assert result == expected_result

    def test_parse_BVT_empty_input(self):
        """テスト区分: UT

        テストカテゴリ: BVT
        テストシナリオ: 空文字列入力の処理確認
        """
        test_doc = """テスト定義:
        - テストカテゴリ: BVT
        - テスト区分: 正常系/UT
        - テストシナリオ: 空文字列入力のテスト
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        result = self.parser.parse("")
        log_msg(f"Result: {result}", LogLevel.DEBUG)

        assert result["request_type"] == "その他"
        assert result["other_info"] == ""

    def test_parse_BVT_long_input(self):
        """テスト区分: UT

        テストカテゴリ: BVT
        テストシナリオ: 長い文字列入力の処理確認
        """
        test_doc = """テスト定義:
        - テストカテゴリ: BVT
        - テスト区分: 正常系/UT
        - テストシナリオ: 長い文字列入力のテスト
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        long_text = "A" * 1000
        result = self.parser.parse(long_text)
        log_msg(f"Result type: {result['request_type']}", LogLevel.DEBUG)

        assert result["request_type"] == "その他"
        assert result["other_info"] == long_text

    def test_parse_BVT_special_chars(self):
        """テスト区分: UT

        テストカテゴリ: BVT
        テストシナリオ: 特殊文字を含む入力の処理確認
        """
        test_doc = """テスト定義:
        - テストカテゴリ: BVT
        - テスト区分: 正常系/UT
        - テストシナリオ: 特殊文字入力のテスト
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        special_chars = "!@#$%^&*()_+"
        result = self.parser.parse(special_chars)
        log_msg(f"Result: {result}", LogLevel.DEBUG)

        assert result["request_type"] == "その他"
        assert result["other_info"] == special_chars


class Test_RemarksParser_remove_leading_dot:
    r"""RemarksParserの_remove_leading_dot()メソッドのテスト

    テスト構造:
    ├── C0: 基本機能テスト
    │   ├── 行頭ドットの削除
    │   └── ドットなし文字列の処理
    │
    ├── C1: 分岐カバレッジ
    │   └── 行頭ドットの有無による分岐
    │       ├── 行頭に全角ドットあり
    │       └── 行頭に全角ドットなし
    │
    ├── C2: 条件組み合わせ
    │   └── 行頭文字のパターン組み合わせ
    │       ├── 行頭が全角ドット
    │       ├── 行頭が半角ドット
    │       ├── 行頭が空白+全角ドット
    │       └── 行中のドット
    │
    └── BVT: 境界値テスト
        ├── 空文字列
        ├── 全角ドットのみ
        └── 連続する全角ドット

    ディシジョンテーブル:
    | No | 条件                           | Case1 | Case2 | Case3 | Case4 | Case5 |
    |----|--------------------------------|-------|-------|-------|-------|-------|
    | 1  | 文字列が空                     | Y     | N     | N     | N     | N     |
    | 2  | 行頭が全角ドット               | N     | Y     | N     | N     | Y     |
    | 3  | 行頭が空白文字                 | N     | N     | Y     | N     | N     |
    | 4  | 行中に全角ドットを含む         | N     | N     | N     | Y     | Y     |
    |出力| 期待される処理                 | 空文字| 削除  | 維持  | 維持  | 混在  |

    境界値検証ケース一覧:
    | ID     | パラメータ | テスト値          | 期待される結果 | テストの目的           | 実装状況                                  |
    |--------|------------|-------------------|----------------|------------------------|-------------------------------------------|
    | BVT_001| line       | ""                | ""             | 空文字列の処理         | test_remove_leading_dot_BVT_empty_string  |
    | BVT_002| line       | "・"              | ""             | 全角ドットのみの処理   | test_remove_leading_dot_BVT_only_dot      |
    | BVT_003| line       | "・・・text"      | "・・text"     | 連続ドットの処理       | test_remove_leading_dot_BVT_multiple_dots |
    | BVT_004| line       | " ・text"         | " ・text"      | 空白+ドットの処理      | test_remove_leading_dot_BVT_space_dot     |
    | BVT_005| line       | "\n・text"        | "\n・text"     | 改行+ドットの処理      | test_remove_leading_dot_BVT_newline_dot   |
    """

    def setup_method(self):
        """テストメソッドの実行前処理"""
        log_msg("test start", LogLevel.INFO)
        self.parser = RemarksParser()

    def teardown_method(self):
        """テストメソッドの実行後処理"""
        log_msg(f"test end\n{'-'*80}\n", LogLevel.INFO)

    def test_remove_leading_dot_C0_basic(self):
        """テスト区分: UT

        テストカテゴリ: C0
        テストシナリオ: 基本的なドット削除処理の確認
        """
        test_doc = """テスト定義:
        - テストカテゴリ: C0
        - テスト区分: 正常系/UT
        - テストシナリオ: 基本的なドット削除のテスト
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        input_text = "・テスト文字列"
        expected = "テスト文字列"
        result = self.parser._remove_leading_dot(input_text)
        log_msg(f"Input: {input_text} -> Output: {result}", LogLevel.DEBUG)

        assert result == expected

    @pytest.mark.parametrize(("input_text", "expected"), [
        ("・テスト文字列", "テスト文字列"),
        ("テスト文字列", "テスト文字列"),
    ])
    def test_remove_leading_dot_C1_branches(self, input_text, expected):
        """テスト区分: UT

        テストカテゴリ: C1
        テストシナリオ: 行頭ドットの有無による分岐の確認
        """
        test_doc = """テスト定義:
        - テストカテゴリ: C1
        - テスト区分: 正常系/UT
        - テストシナリオ: 行頭ドットの有無による分岐テスト
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)
        log_msg(f"Input: {input_text}", LogLevel.DEBUG)

        result = self.parser._remove_leading_dot(input_text)
        log_msg(f"Result: {result}", LogLevel.DEBUG)

        assert result == expected

    @pytest.mark.parametrize(("input_text", "expected"), [
        ("・テスト文字列", "テスト文字列"),
        (".テスト文字列", ".テスト文字列"),
        (" ・テスト文字列", " ・テスト文字列"),
        ("テスト・文字列", "テスト・文字列"),
    ])
    def test_remove_leading_dot_C2_combinations(self, input_text, expected):
        """テスト区分: UT

        テストカテゴリ: C2
        テストシナリオ: 行頭文字のパターン組み合わせテスト
        """
        test_doc = """テスト定義:
        - テストカテゴリ: C2
        - テスト区分: 正常系/UT
        - テストシナリオ: 行頭文字のパターン組み合わせテスト
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)
        log_msg(f"Input: {input_text}", LogLevel.DEBUG)

        result = self.parser._remove_leading_dot(input_text)
        log_msg(f"Result: {result}", LogLevel.DEBUG)

        assert result == expected

    def test_remove_leading_dot_BVT_empty_string(self):
        """テスト区分: UT

        テストカテゴリ: BVT
        テストシナリオ: 空文字列入力の処理確認
        """
        test_doc = """テスト定義:
        - テストカテゴリ: BVT
        - テスト区分: 正常系/UT
        - テストシナリオ: 空文字列入力のテスト
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        result = self.parser._remove_leading_dot("")
        log_msg(f"Result: '{result}'", LogLevel.DEBUG)

        assert result == ""

    def test_remove_leading_dot_BVT_only_dot(self):
        """テスト区分: UT

        テストカテゴリ: BVT
        テストシナリオ: 全角ドットのみの入力処理確認
        """
        test_doc = """テスト定義:
        - テストカテゴリ: BVT
        - テスト区分: 正常系/UT
        - テストシナリオ: 全角ドットのみの入力テスト
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        result = self.parser._remove_leading_dot("・")
        log_msg(f"Result: '{result}'", LogLevel.DEBUG)

        assert result == ""

    def test_remove_leading_dot_BVT_multiple_dots(self):
        """テスト区分: UT

        テストカテゴリ: BVT
        テストシナリオ: 連続する全角ドットの処理確認
        """
        test_doc = """テスト定義:
        - テストカテゴリ: BVT
        - テスト区分: 正常系/UT
        - テストシナリオ: 連続する全角ドットの処理テスト
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        result = self.parser._remove_leading_dot("・・・テスト")
        log_msg(f"Result: {result}", LogLevel.DEBUG)

        assert result == "・・テスト"

class Test_RemarksParser_process_sales_department:
    r"""RemarksParserの_process_sales_department()メソッドのテスト

    テスト構造:
    ├── C0: 基本機能テスト
    │   ├── 支店営業部パターン
    │   └── 営業部営業部パターン
    │
    ├── C1: 分岐カバレッジ
    │   ├── 正規表現マッチ成功
    │   │   ├── 支店+営業部パターン
    │   │   ├── 支店+営業第n部パターン
    │   │   ├── 営業部+営業部パターン
    │   │   └── 営業部+営業第n部パターン
    │   └── 正規表現マッチ失敗
    │
    ├── C2: 条件組み合わせ
    │   └── 営業部名パターンの組み合わせ
    │       ├── 支店名の種類 (漢字/カナ/英数字)
    │       └── 営業部名の種類
    │
    └── BVT: 境界値テスト
        ├── 文字列長の境界
        └── 特殊パターン

    ディシジョンテーブル:
    | No | 条件                           | Case1 | Case2 | Case3 | Case4 | Case5 |
    |----|--------------------------------|-------|-------|-------|-------|-------|
    | 1  | 支店パターンを含む             | Y     | N     | Y     | N     | N     |
    | 2  | 営業部パターンを含む           | N     | Y     | N     | Y     | N     |
    | 3  | 営業第n部を含む                | N     | N     | Y     | Y     | N     |
    | 4  | 不正なフォーマット             | N     | N     | N     | N     | Y     |
    |出力| 解析成功                       | Y     | Y     | Y     | Y     | N     |

    境界値検証ケース一覧:
    | ID     | パラメータ | テスト値                     | 期待される結果    | テストの目的          | 実装状況                                             |
    |--------|------------|------------------------------|-------------------|-----------------------|------------------------------------------------------|
    | BVT_001| line       | ""                           | 解析失敗          | 空文字列の処理        | test_process_sales_department_BVT_empty_string       |
    | BVT_002| line       | "支店営業部"                 | 解析失敗          | 支店名なしの処理      | test_process_sales_department_BVT_no_branch_name     |
    | BVT_003| line       | "あ" * 50 + "支店営業部"     | 解析成功          | 長い支店名の処理      | test_process_sales_department_BVT_long_name          |
    | BVT_004| line       | "営業営業部営業部"           | 解析成功          | 重複キーワードの処理  | test_process_sales_department_BVT_duplicate_keywords |
    | BVT_005| line       | "ABC支店営業第123部"         | 解析成功          | 英数字混在の処理      | test_process_sales_department_BVT_alphanumeric       |
    """

    def setup_method(self):
        """テストメソッドの実行前処理"""
        log_msg("test start", LogLevel.INFO)
        self.parser = RemarksParser()

    def teardown_method(self):
        """テストメソッドの実行後処理"""
        log_msg(f"test end\n{'-'*80}\n", LogLevel.INFO)

    def test_process_sales_department_C0_basic(self):
        """テスト区分: UT

        テストカテゴリ: C0
        テストシナリオ: 基本的な営業部署パターンの処理確認
        """
        test_doc = """テスト定義:
        - テストカテゴリ: C0
        - テスト区分: 正常系/UT
        - テストシナリオ: 基本的な営業部署パターンのテスト
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        input_text = "八重洲通支店営業部"
        self.parser._process_sales_department(input_text)
        log_msg(f"Input: {input_text}", LogLevel.DEBUG)
        log_msg(f"Result: {self.parser.result}", LogLevel.DEBUG)

        assert self.parser.result["request_type"] == "営業部傘下"
        assert self.parser.result["sales_department"]["branch_name"] == "八重洲通支店"
        assert self.parser.result["sales_department"]["department_name"] == "営業部"

    @pytest.mark.parametrize(("input_text", "expected_branch", "expected_dept"), [
        ("八重洲通支店営業部", "八重洲通支店", "営業部"),
        ("笹島支店営業第一部", "笹島支店", "営業第一部"),
        ("大阪営業部営業部", "大阪営業部", "営業部"),
        ("東京営業部営業第二部", "東京営業部", "営業第二部"),
    ])
    def test_process_sales_department_C1_branches(self, input_text, expected_branch, expected_dept):
        """テスト区分: UT

        テストカテゴリ: C1
        テストシナリオ: 営業部署名パターンの分岐確認
        """
        test_doc = """テスト定義:
        - テストカテゴリ: C1
        - テスト区分: 正常系/UT
        - テストシナリオ: 営業部署名パターンの分岐テスト
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)
        log_msg(f"Input: {input_text}", LogLevel.DEBUG)

        self.parser._process_sales_department(input_text)
        log_msg(f"Result: {self.parser.result}", LogLevel.DEBUG)

        assert self.parser.result["request_type"] == "営業部傘下"
        assert self.parser.result["sales_department"]["branch_name"] == expected_branch
        assert self.parser.result["sales_department"]["department_name"] == expected_dept

    @pytest.mark.parametrize(("input_text", "expected_branch", "expected_dept"), [
        ("八重洲通支店営業部", "八重洲通支店", "営業部"),
        ("ヨコハマ支店営業第一部", "ヨコハマ支店", "営業第一部"),
        ("ABC営業部営業部", "ABC営業部", "営業部"),
        ("新宿営業部営業第123部", "", ""),   # match(2)に空振り,値取得なし/インプット想定外
        ("新宿営業部", "", ""),              # match(2)に空振り,値取得なし/インプット想定外
    ])
    def test_process_sales_department_C2_combinations(self, input_text, expected_branch, expected_dept):
        """テスト区分: UT

        テストカテゴリ: C2
        テストシナリオ: 営業部署名の文字種組み合わせ確認
        """
        test_doc = """テスト定義:
        - テストカテゴリ: C2
        - テスト区分: 正常系/UT
        - テストシナリオ: 営業部署名の文字種組み合わせテスト
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)
        log_msg(f"Input: {input_text}", LogLevel.DEBUG)

        self.parser._process_sales_department(input_text)
        log_msg(f"Result: {self.parser.result}", LogLevel.DEBUG)

        assert self.parser.result["request_type"] == "営業部傘下"
        assert self.parser.result["sales_department"]["branch_name"] == expected_branch
        assert self.parser.result["sales_department"]["department_name"] == expected_dept

    def test_process_sales_department_BVT_empty_string(self):
        """テスト区分: UT

        テストカテゴリ: BVT
        テストシナリオ: 空文字列の処理確認
        """
        test_doc = """テスト定義:
        - テストカテゴリ: BVT
        - テスト区分: 正常系/UT
        - テストシナリオ: 空文字列の処理テスト
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        self.parser._process_sales_department("")
        log_msg(f"Result: {self.parser.result}", LogLevel.DEBUG)

        assert self.parser.result["request_type"] == "営業部傘下"
        assert self.parser.result["sales_department"]["branch_name"] == ""
        assert self.parser.result["sales_department"]["department_name"] == ""

    def test_process_sales_department_BVT_long_name(self):
        """テスト区分: UT

        テストカテゴリ: BVT
        テストシナリオ: 長い支店名の処理確認
        """
        test_doc = """テスト定義:
        - テストカテゴリ: BVT
        - テスト区分: 正常系/UT
        - テストシナリオ: 長い支店名の処理テスト
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        long_name = "あ" * 50
        input_text = f"{long_name}支店営業部"
        log_msg(f"Input: {input_text}", LogLevel.DEBUG)

        self.parser._process_sales_department(input_text)
        log_msg(f"Result: {self.parser.result}", LogLevel.DEBUG)

        assert self.parser.result["request_type"] == "営業部傘下"
        assert self.parser.result["sales_department"]["branch_name"] == f"{long_name}支店"
        assert self.parser.result["sales_department"]["department_name"] == "営業部"

    def test_process_sales_department_BVT_duplicate_keywords(self):
        """テスト区分: UT

        テストカテゴリ: BVT
        テストシナリオ: 重複キーワードを含む処理確認
        """
        test_doc = """テスト定義:
        - テストカテゴリ: BVT
        - テスト区分: 正常系/UT
        - テストシナリオ: 重複キーワードを含む処理テスト
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        input_text = "営業営業部営業部"
        log_msg(f"Input: {input_text}", LogLevel.DEBUG)

        self.parser._process_sales_department(input_text)
        log_msg(f"Result: {self.parser.result}", LogLevel.DEBUG)

        assert self.parser.result["request_type"] == "営業部傘下"
        assert self.parser.result["sales_department"]["branch_name"] == "営業営業部"
        assert self.parser.result["sales_department"]["department_name"] == "営業部"

class Test_RemarksParser_process_area_group:
    """RemarksParserの_process_area_group()メソッドのテスト

    テスト構造:
    ├── C0: 基本機能テスト
    │   ├── 設立日なしパターン
    │   └── 設立日ありパターン
    │
    ├── C1: 分岐カバレッジ
    │   ├── 正規表現マッチ成功
    │   │   ├── コード + Gr名
    │   │   └── コード + Gr名 + 設立日
    │   └── 正規表現マッチ失敗
    │
    ├── C2: 条件組み合わせ
    │   ├── エリアコードのパターン
    │   │   ├── 数字のみ
    │   │   ├── アルファベットのみ
    │   │   └── 英数字混在
    │   └── Gr名のパターン
    │       ├── 日本語
    │       ├── 英数字
    │       └── 記号
    │
    └── BVT: 境界値テスト
        ├── コードの長さ
        ├── 区切り文字
        └── 設立日フォーマット

    ディシジョンテーブル:
    | No | 条件                           | Case1 | Case2 | Case3 | Case4 | Case5 |
    |----|--------------------------------|-------|-------|-------|-------|-------|
    | 1  | 5桁のコードが存在              | Y     | Y     | N     | Y     | N     |
    | 2  | Gr名が存在                     | Y     | Y     | Y     | N     | N     |
    | 3  | 設立日が存在                   | N     | Y     | -     | -     | -     |
    | 4  | 正しい区切り文字               | Y     | Y     | -     | -     | -     |
    |出力| 解析成功                       | Y     | Y     | N     | N     | N     |

    境界値検証ケース一覧:
    | ID     | パラメータ | テスト値                    | 期待される結果            | テストの目的              | 実装状況                                 |
    |--------|------------|-----------------------------|---------------------------|---------------------------|------------------------------------------|
    | BVT_001| line       | ""                          | 解析失敗                  | 空文字列の処理            | test_process_area_group_BVT_empty_string |
    | BVT_002| line       | "1234 TestGr"               | 解析失敗                  | 4桁コードの処理           | test_process_area_group_BVT_short_code   |
    | BVT_003| line       | "123456 TestGr"             | 解析失敗                  | 6桁コードの処理           | test_process_area_group_BVT_long_code    |
    | BVT_004| line       | "12345　TestGr"             | 解析成功                  | 全角スペースの処理        | test_process_area_group_BVT_full_space   |
    | BVT_005| line       | "12345TestGr"               | 解析失敗                  | スペースなしの処理        | test_process_area_group_BVT_no_space     |
    """

    def setup_method(self):
        """テストメソッドの実行前処理"""
        log_msg("test start", LogLevel.INFO)
        self.parser = RemarksParser()

    def teardown_method(self):
        """テストメソッドの実行後処理"""
        log_msg(f"test end\n{'-'*80}\n", LogLevel.INFO)

    def test_process_area_group_C0_basic(self):
        """テスト区分: UT

        テストカテゴリ: C0
        テストシナリオ: 基本的なエリアグループパターンの処理確認
        """
        test_doc = """テスト定義:
        - テストカテゴリ: C0
        - テスト区分: 正常系/UT
        - テストシナリオ: 基本的なエリアグループパターンのテスト
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        input_text = "41002 東日本第一Gr"
        log_msg(f"Input: {input_text}", LogLevel.DEBUG)

        self.parser._process_area_group(input_text)
        log_msg(f"Result: {self.parser.result}", LogLevel.DEBUG)

        assert self.parser.result["request_type"] == "エリア"
        assert self.parser.result["area_group"]["group_code"] == "41002"
        assert self.parser.result["area_group"]["group_name"] == "東日本第一Gr"
        assert self.parser.result["area_group"]["established_date"] == ""

    @pytest.mark.parametrize(("input_text", "expected_code", "expected_name", "expected_date"), [
        ("41002 東日本第一Gr", "41002", "東日本第一Gr", ""),
        ("41012 グローバル財務戦略Gr (4/1新設)", "41012", "グローバル財務戦略Gr", "4/1新設"),
        ("41002　東日本第一Gr", "41002", "東日本第一Gr", ""),  # 全角スペース
    ])
    def test_process_area_group_C1_branches(self, input_text, expected_code, expected_name, expected_date):
        """テスト区分: UT

        テストカテゴリ: C1
        テストシナリオ: エリアグループパターンの分岐確認
        """
        test_doc = """テスト定義:
        - テストカテゴリ: C1
        - テスト区分: 正常系/UT
        - テストシナリオ: エリアグループパターンの分岐テスト
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)
        log_msg(f"Input: {input_text}", LogLevel.DEBUG)

        self.parser._process_area_group(input_text)
        log_msg(f"Result: {self.parser.result}", LogLevel.DEBUG)

        assert self.parser.result["request_type"] == "エリア"
        assert self.parser.result["area_group"]["group_code"] == expected_code
        assert self.parser.result["area_group"]["group_name"] == expected_name
        assert self.parser.result["area_group"]["established_date"] == expected_date

    @pytest.mark.parametrize(("input_text", "expected_code", "expected_name", "expected_date"), [
        # 基本パターン(英数字のみ)
        ("12345 TestGr", "12345", "TestGr", ""),
        # 日本語を含むパターン
        ("ABCD1 日本語Gr", "ABCD1", "日本語Gr", ""),
        ("1A2B3 東京支社Gr", "1A2B3", "東京支社Gr", ""),
        # 特殊文字を含むパターン
        ("41012 特殊!#$Gr (新設)", "41012", "特殊!#$Gr", "新設"),
        ("41013 営業部-1Gr", "41013", "営業部-1Gr", ""),
        # 複合パターン
        ("41014 東京_海外#1Gr (4/1移管)", "41014", "東京_海外#1Gr", "4/1移管"),
    ])
    def test_process_area_group_C2_combinations(self, input_text, expected_code, expected_name, expected_date):
        r"""テスト区分: UT

        テストカテゴリ: C2
        テストシナリオ: エリアグループ情報の文字種組み合わせ確認

        条件の組み合わせ:
        1. コードパターン(\w{5})
            - 数字のみ(例:12345)
            - 英字のみ(例:ABCD1)
            - 英数字混在(例:1A2B3)

        2. グループ名パターン([^\s]+?Gr)
            - 英数字のみ(例:TestGr)
            - 日本語を含む(例:日本語Gr)
            - 特殊文字を含む(例:特殊!#$Gr)
            - ハイフンを含む(例:営業部-1Gr)
            - アンダースコアを含む(例:東京_海外Gr)

        3. 設立日パターン(\(.*?\))
            - なし
            - シンプルな日付(例:(新設))
            - 詳細な情報(例:(4/1移管))
        """
        test_doc = """テスト定義:
        - テストカテゴリ: C2
        - テスト区分: 正常系/UT
        - テストシナリオ: エリアグループ情報の文字種組み合わせテスト
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)
        log_msg(f"Input: {input_text}", LogLevel.DEBUG)

        self.parser._process_area_group(input_text)
        log_msg(f"Result: {self.parser.result}", LogLevel.DEBUG)

        assert self.parser.result["request_type"] == "エリア"
        assert self.parser.result["area_group"]["group_code"] == expected_code
        assert self.parser.result["area_group"]["group_name"] == expected_name
        assert self.parser.result["area_group"]["established_date"] == expected_date

    def test_process_area_group_BVT_empty_string(self):
        """テスト区分: UT

        テストカテゴリ: BVT
        テストシナリオ: 空文字列の処理確認
        """
        test_doc = """テスト定義:
        - テストカテゴリ: BVT
        - テスト区分: 正常系/UT
        - テストシナリオ: 空文字列の処理テスト
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        self.parser._process_area_group("")
        log_msg(f"Result: {self.parser.result}", LogLevel.DEBUG)

        assert self.parser.result["request_type"] == "エリア"
        assert self.parser.result["area_group"]["group_code"] == ""
        assert self.parser.result["area_group"]["group_name"] == ""
        assert self.parser.result["area_group"]["established_date"] == ""

    def test_process_area_group_BVT_full_space(self):
        """テスト区分: UT

        テストカテゴリ: BVT
        テストシナリオ: 全角スペース区切りの処理確認
        """
        test_doc = """テスト定義:
        - テストカテゴリ: BVT
        - テスト区分: 正常系/UT
        - テストシナリオ: 全角スペース区切りの処理テスト
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        input_text = "41002　東日本第一Gr"  # 全角スペース
        log_msg(f"Input: {input_text}", LogLevel.DEBUG)

        self.parser._process_area_group(input_text)
        log_msg(f"Result: {self.parser.result}", LogLevel.DEBUG)

        assert self.parser.result["request_type"] == "エリア"
        assert self.parser.result["area_group"]["group_code"] == "41002"
        assert self.parser.result["area_group"]["group_name"] == "東日本第一Gr"

    def test_process_area_group_BVT_invalid_patterns(self):
        """テスト区分: UT

        テストカテゴリ: BVT
        テストシナリオ: 不正なパターンの処理確認
        """
        test_doc = """テスト定義:
        - テストカテゴリ: BVT
        - テスト区分: 異常系/UT
        - テストシナリオ: 不正なパターンの処理テスト
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        test_patterns = [
            "1234 TestGr",    # 4桁コード
            "123456 TestGr",  # 6桁コード
            "12345TestGr",    # スペースなし
            "12345 Test",     # Grなし
        ]

        for pattern in test_patterns:
            log_msg(f"Testing pattern: {pattern}", LogLevel.DEBUG)
            self.parser._process_area_group(pattern)
            assert self.parser.result["area_group"]["group_code"] == ""
            assert self.parser.result["area_group"]["group_name"] == ""

