"""テスト実施方法

# project topディレクトリから実行する
$ pwd
/developer/library_dev/project_1

# pytest結果をファイル出力する場合
$ pytest -lv ./tests/lib/common_utils/test_ibr_csv_helper.py > tests/log/pytest_result.log

# pytest結果を標準出力する場合
$ pytest -lv ./tests/lib/common_utils/test_ibr_csv_helper.py
"""
from pathlib import Path
from unittest.mock import MagicMock

import pandas as pd
import pytest

from src.lib.converter_utils.ibr_excel_field_analyzer import (
    RemarksParser,
)

from src.lib.common_utils.ibr_enums import LogLevel
from src.lib.common_utils.ibr_get_config import Config

# 呼び出し元
package_path = Path(__file__)
config = Config.load(package_path)

log_msg = config.log_message
log_msg(str(config), LogLevel.DEBUG)

class Test_RemarksParser:
    """RemarksParser Classのテスト全体をまとめたClass

    RemarksParser.parse()
    │
    ├─ C0(命令網羅)
    │   └─ 基本的な解析処理
    │       ├─ 営業部署情報の解析
    │       ├─ エリアグループ情報の解析
    │       └─ その他の情報の解析
    │
    ├─ C1(分岐網羅)
    │   ├─ 営業部署情報の分岐
    │   │   ├─ 通常の営業部
    │   │   └─ 数字付きの営業部
    │   ├─ エリアグループ情報の分岐
    │   │   ├─ 設立日あり
    │   │   └─ 設立日なし
    │   └─ その他の情報の分岐
    │       └─ 変更、廃止を含む情報
    │
    └─ C2(条件網羅)
        ├─ 入力テキストの種類
        │   ├─ 営業部署情報のみ
        │   ├─ エリアグループ情報のみ
        │   └─ その他の情報のみ
        └─ 特殊なケース
            ├─ 空の入力
            └─ 複数行の入力
    """
    def setup_method(self):
        log_msg("test start", LogLevel.INFO)

    def teardown_method(self):
        log_msg(f"test end\n{'-'*80}\n", LogLevel.INFO)

    @pytest.mark.parametrize(
        ("remarks_text", "expected_result"),
        [
            (
                "八重洲通支店営業部",
                {
                    "request_type": "営業部傘下",
                    "sales_department": {
                        "department_name": "八重洲通支店営業部",
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
                "笹島支店第一営業部",
                {
                    "request_type": "営業部傘下",
                    "sales_department": {
                        "department_name": "笹島支店第一営業部",
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
        ],
    )
    def test_parse_UT_C0_normal_case(self, remarks_text, expected_result):
        test_doc = """テスト定義:

        - テストカテゴリ: C0
        - テスト区分: 正常系/UT
        - テストシナリオ: RemarksParserの基本的な解析処理の確認
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        # インスタンス生成
        parser = RemarksParser()

        # 結果定義,関数実行
        result = parser.parse(remarks_text)

        log_msg(f'Input text: {remarks_text}', LogLevel.DEBUG)
        log_msg(f'Expected result: {expected_result}', LogLevel.DEBUG)
        log_msg(f'Actual result: {result}', LogLevel.DEBUG)

        # 結果評価
        assert result == expected_result, f"Expected {expected_result}, but got {result}"


class Test_RemarksParser_init:
    """RemarksParserの__init__メソッドのテスト全体をまとめたClass

    RemarksParser.__init__()
    │
    ├─ C0(命令網羅)
    │   └─ 基本的なインスタンス生成
    │       └─ result辞書が正しく初期化されているか
    │           ├─ request_typeが空文字列
    │           ├─ sales_departmentが正しい構造
    │           ├─ area_groupが正しい構造
    │           └─ other_infoが空文字列
    │
    ├─ C1(分岐網羅)
    │   └─ (__init__メソッドには明示的な分岐がないため、該当なし)
    │
    └─ C2(条件網羅)
        ├─ 正常系
        │   ├─ 型チェック
        │   │   ├─ resultがdict型
        │   │   ├─ sales_departmentがdict型
        │   │   └─ area_groupがdict型
        │   └─ 各フィールドの初期値確認
        │       ├─ sales_department
        │       │   ├─ department_nameが空文字列
        │       │   └─ branch_nameが空文字列
        │       └─ area_group
        │           ├─ group_codeが空文字列
        │           ├─ group_nameが空文字列
        │           └─ established_dateが空文字列
        │
        └─ 異常系
            ├─ 引数ありでインスタンス生成(引数は想定外)
            └─ メモリ不足状態でのインスタンス生成
    """

    @pytest.fixture()
    def remarks_parser(self):
        return RemarksParser()

    def setup_method(self):
        log_msg("test start", LogLevel.INFO)

    def teardown_method(self):
        log_msg(f"test end\n{'-'*80}\n", LogLevel.INFO)


    def test_init_C0_basic_instance_creation(self, remarks_parser):
        test_doc = """テスト定義:

        - テストカテゴリ: C0
        - テスト区分: 正常系/UT
        - テストシナリオ: 基本的なインスタンス生成と結果辞書の初期化確認

        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        log_msg(f'Result dictionary: {remarks_parser.result}', LogLevel.DEBUG)

        # インスタンス生成して内部メソッドは何も呼び出していない状態
        assert remarks_parser.result["request_type"] == ""
        assert "sales_department" in remarks_parser.result
        assert "area_group" in remarks_parser.result
        assert remarks_parser.result["other_info"] == ""
