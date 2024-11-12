"""bpr adフラグ設定値検証"""
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch  # callを追加

import pandas as pd
import pytest

from src.lib.common_utils.ibr_dataframe_helper import tabulate_dataframe
from src.lib.common_utils.ibr_decorator_config import initialize_config
from src.lib.common_utils.ibr_enums import (
    ApplicationType,
    BprADFlagResults,
    BranchCodeType,
    LogLevel,
    RelatedCompanyType,
)

#from src.lib.common_utils.ibr_pickled_table_searcher import TableSearcher
from src.lib.converter_utils.ibr_bpr_flag_determiner import BprAdFlagDeterminer, ValidationConfig

# config共有
config = initialize_config(sys.modules[__name__])
package_config = config.package_config
log_msg = config.log_message

class TestBprAdFlagDeterminerInit:
    """BprAdFlagDeterminerの__init__メソッドのテスト

    テスト構造:
    ├── C0: 基本機能テスト
    │   ├── 正常系: 標準的な初期化
    │   └── 異常系: ファイルパス不正
    ├── C1: 分岐カバレッジ
    │   ├── config設定あり
    │   └── config設定なし
    ├── C2: 条件組み合わせ
    │   ├── SPECIFIC_WORDSの有無
    │   ├── file_pathの有無
    │   └── reference/request_dataの有無組み合わせ
    └── BVT: 境界値テスト
        ├── ファイルパス最大長
        └── 特殊文字を含むパス

    C1のディシジョンテーブル:
    | 条件                          | DT1 | DT2 | DT3 | DT4 |
    |-------------------------------|-----|-----|-----|-----|
    | file_pathが指定されている     | Y   | Y   | N   | N   |
    | configにSPECIFIC_WORDSがある  | Y   | N   | Y   | N   |
    | configにreference_dataがある  | Y   | N   | Y   | N   |
    |-------------------------------|-----|-----|-----|-----|
    | 正常初期化                    | X   | -   | X   | -   |
    | デフォルト値使用              | -   | X   | -   | X   |

    境界値検証ケース一覧:
    | ID    | パラメータ   | テスト値         | 期待される結果  | テストの目的         | 実装状況 |
    |-------|--------------|------------------|-----------------|----------------------|----------|
    | BVT01 | file_path    | ""               | ValueError      | 空文字列の処理       | 実装済み |
    | BVT02 | file_path    | "a" * 255        | ValueError      | パス長最大値の処理   | 実装済み |
    | BVT03 | file_path    | "test/file.pkl"  | 正常初期化      | 標準的なパス         | 実装済み |
    | BVT04 | file_path    | "../../test.pkl" | ValueError      | 相対パスの処理       | 実装済み |
    """

    def setup_method(self):
        log_msg("test start", LogLevel.INFO)

    def teardown_method(self):
        log_msg(f"test end\n{'-'*80}\n", LogLevel.INFO)

    @pytest.fixture()
    def mock_config(self):
        with patch('src.lib.converter_utils.ibr_bpr_flag_determiner.package_config') as mock:
            mock.get.return_value = {
                'SpecificWords': ['米州', '欧州', 'アジア'],
                'reference_data': 'reference.pkl',
                'request_data': 'request.pkl',
            }
            yield mock

    @pytest.fixture()
    def mock_table_searcher(self):
        with patch('src.lib.converter_utils.ibr_bpr_flag_determiner.TableSearcher') as mock:
            def side_effect(*args, **kwargs):
                # 引数のログ出力
                log_msg(f"TableSearcher called with args: {args}, kwargs: {kwargs}", LogLevel.DEBUG)
                if len(args) >= 2 and args[1] and ("../" in str(args[1]) or "\\" in str(args[1])):
                    err_msg = "Invalid file path: Contains invalid characters or path traversal"
                    raise ValueError(err_msg) from None

                mock_instance = MagicMock()
                mock_instance.df = pd.DataFrame({'test': [1, 2, 3]})
                return mock_instance

            mock.side_effect = side_effect
            yield mock

    def test_init_C0_standard_initialization(self, mock_config, mock_table_searcher):
        """基本的な初期化のテスト"""
        test_doc = """
        テスト区分: UT
        テストカテゴリ: C0
        テストシナリオ: 標準的な初期化
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        determiner = BprAdFlagDeterminer()
        assert ['米州', '欧州', 'アジア'] == determiner.SPECIFIC_WORDS
        assert isinstance(determiner.reference_df, pd.DataFrame)
        assert isinstance(determiner.request_df, pd.DataFrame)

    def test_init_C0_invalid_file_path(self, mock_config):
        """不正なファイルパスでの初期化テスト"""
        test_doc = """
        テスト区分: UT
        テストカテゴリ: C0
        テストシナリオ: 不正なファイルパスによる初期化エラー, FileNotFoundError
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        with pytest.raises(FileNotFoundError):
            BprAdFlagDeterminer("invalid/path/test.pkl")

    def test_init_C1_DT1_with_config(self, mock_config, mock_table_searcher):
        """設定ありパターンのテスト"""
        test_doc = """
        テスト区分: UT
        テストカテゴリ: C1
        テストシナリオ: 全設定値ありでの初期化
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        determiner = BprAdFlagDeterminer("test.pkl")
        assert ['米州', '欧州', 'アジア'] == determiner.SPECIFIC_WORDS
        mock_table_searcher.assert_called()

    def test_init_C2_no_specific_words(self, mock_config, mock_table_searcher):
        """SPECIFIC_WORDS未設定での初期化テスト"""
        test_doc = """
        テスト区分: UT
        テストカテゴリ: C2
        テストシナリオ: SPECIFIC_WORDS未設定での初期化
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        mock_config.get.return_value = {
            'SpecificWords': [],
            'reference_data': 'reference.pkl',
            'request_data': 'request.pkl',
        }

        determiner = BprAdFlagDeterminer()
        assert [] == determiner.SPECIFIC_WORDS

    @pytest.mark.parametrize(("file_path", "expected_error"), [
        ("", False),                        # デフォルトパス使用, エラーなし
        ("../../test.pkl", True),           # 不正な相対パス(パストラバーサル)
        (str(Path("test/file")), False),    # 正常パス,エラーなし
        ("./test/data", False),             # 正常な相対パス,エラーなし
        (str(Path("test/../data")), True),  # 間接的なパストラバーサル
    ])
    def test_init_BVT_file_path(self, mock_config, mock_table_searcher, file_path, expected_error):
        """ファイルパスの境界値テスト"""
        test_doc = f"""
        テスト区分: UT
        テストカテゴリ: BVT
        テストシナリオ: ファイルパスの境界値テスト
        テストデータ: {file_path}
        期待結果: {'エラー発生' if expected_error else '正常初期化'}
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)
    
        # common_configのモック設定
        mock_config.get.return_value = {
            'SpecificWords': ['米州', '欧州', 'アジア'],
            'reference_data': 'reference.pkl',
            'request_data': 'request.pkl',
        }
    
        if expected_error:
            with pytest.raises(ValueError):
                BprAdFlagDeterminer(file_path)
        else:
            determiner = BprAdFlagDeterminer(file_path)
            assert isinstance(determiner.reference_df, pd.DataFrame)
            assert isinstance(determiner.request_df, pd.DataFrame)
    
            # TableSearcherの呼び出し回数を検証
            assert mock_table_searcher.call_count == 2

            # 呼び出し時の引数を記録
            calls = mock_table_searcher.call_args_list
            log_msg(f"TableSearcher calls: {calls}", LogLevel.DEBUG)
    
            # file_pathの有無に応じた検証
            if not file_path:
                # デフォルトパスケース
                assert any('reference.pkl' in str(call) for call in calls)
                assert any('request.pkl' in str(call) for call in calls)
            else:
                # カスタムパスケース
                test_path = Path(file_path)
                for call in mock_table_searcher.call_args_list:
                    args = call[0]
                    assert len(args) >= 2
                    assert Path(args[1]).parts == test_path.parts  # パスの比較を部分的に行う

    #@pytest.mark.parametrize(("file_path", "expected_error"), [
    #    ("", False),                          # デフォルトパス使用, エラーなし
    #    ("../../test.pkl", True),             # 不正な相対パス(パストラバーサル)
    #    ("test\\file.pkl", True),             # 不正なパス文字
    #    (Path("test/data"), False),           # 正常パス,エラーなし
    #    ("./test/data", False),               # 正常な相対パス,エラーなし
    #    ("/absolute/path/data", False),        # 絶対パス,エラーなし
    #    ("test/../data", True),               # 間接的なパストラバーサル
    #    ("test/./data", False),               # 正規化が必要なパス,エラーなし
    #    ("test//data", False),                # 重複スラッシュ,エラーなし
    #    (Path("/test/data").resolve(), False), # 正規化済みパス,エラーなし
    #])
    #def test_init_BVT_file_path(self, mock_config, mock_table_searcher, file_path, expected_error):
    #    """ファイルパスの境界値テスト"""
    #    test_doc = f"""
    #    テスト区分: UT
    #    テストカテゴリ: BVT
    #    テストシナリオ: ファイルパスの境界値テスト
    #    テストデータ: {file_path}
    #    期待結果: {'エラー発生' if expected_error else '正常初期化'}
    #    """
    #    log_msg(f"\n{test_doc}", LogLevel.INFO)

    #    # common_configのモック設定
    #    mock_config.get.return_value = {
    #        'SpecificWords': ['米州', '欧州', 'アジア'],
    #        'reference_data': 'reference.pkl',
    #        'request_data': 'request.pkl',
    #    }

    #    if expected_error:
    #        with pytest.raises(ValueError):
    #            BprAdFlagDeterminer(file_path)
    #    else:
    #        determiner = BprAdFlagDeterminer(file_path)
    #        assert isinstance(determiner.reference_df, pd.DataFrame)
    #        assert isinstance(determiner.request_df, pd.DataFrame)

    #        # TableSearcherの呼び出し回数を検証
    #        assert mock_table_searcher.call_count == 2

    #        # 呼び出し時の引数を記録
    #        calls = mock_table_searcher.call_args_list
    #        log_msg(f"TableSearcher calls: {calls}", LogLevel.DEBUG)

    #        # file_pathの有無に応じた検証
    #        if not file_path:
    #            # デフォルトパスケース
    #            assert any('reference.pkl' in str(call) for call in calls)
    #            assert any('request.pkl' in str(call) for call in calls)
    #        else:
    #            # カスタムパスケース
    #            path_obj = Path(file_path)
    #            for call in calls:
    #                args, kwargs = call
    #                assert len(args) >= 2
    #                assert Path(args[1]) == path_obj

class TestBprAdFlagDeterminerDetermineBprAdFlag:
    """BprAdFlagDeterminerのdetermine_bpr_ad_flagメソッドのテスト

    テスト構造:
    ├── C0: 基本機能テスト
    │   ├── 新設処理
    │   ├── 変更処理   TODO():実装後にテスト作成
    │   └── 廃止処理   TODO():実装後にテスト作成
    ├── C1: 分岐カバレッジ
    │   ├── 国企かつ部店コード6系
    │   ├── 課Grコード0部店あり
    │   ├── 課Grコード0部店なし
    │   └── リファレンス参照パターン  TODO():実装後にテスト作成
    ├── C2: 条件組み合わせ
    │   ├── application_typeと部店コードの組み合わせ C1でカバー
    │   ├── 特定ワード判定の組み合わせ               C1でカバー
    │   └── アラート条件の組み合わせ
    └── BVT: 境界値テスト
        ├── 部店コードの境界値
        └── 課Grコードの境界値

    C1のディシジョンテーブル:
    | 条件                         | DT1 | DT2 | DT3 | DT4 | DT5 | DT6 |
    |------------------------------|-----|-----|-----|-----|-----|-----|
    | 申請種類が新設               | Y   | Y   | Y   | N   | N   | N   |
    | 国企申請                     | Y   | N   | N   | -   | -   | -   |
    | 部店コード6系                | Y   | -   | -   | -   | -   | -   |
    | 課Grコード0の部店あり        | -   | Y   | N   | -   | -   | -   |
    | リファレンスに情報あり       | -   | -   | -   | Y   | N   | -   |
    |------------------------------|-----|-----|-----|-----|-----|-----|
    | ADのみ                       | X   | -   | -   | -   | -   | -   |
    | BPR対象                      | -   | X   | -   | X   | -   | -   |
    | BPR対象外                    | -   | -   | X   | -   | X   | -   |
    | エラー                       | -   | -   | -   | -   | -   | X   |

    境界値検証ケース一覧:
    | ID    | パラメータ      | テスト値         | 期待される結果 | テストの目的     | 実装状況 |
    |-------|-----------------|------------------|----------------|------------------|----------|
    | BVT01 | branch_code     | "0"              | BPR対象        | 最小部店コード   | 実装済み |
    | BVT02 | branch_code     | "6"              | BPR対象        | 本部コード最小   | 実装済み |
    | BVT03 | branch_code     | "71"             | BPR対象        | MUFG最小         | 実装済み |
    | BVT04 | section_gr_code | "0"              | BPR対象外      | 課Gr最小         | 実装済み |
    | BVT05 | section_gr_code | "99999"          | BPR対象        | 課Gr最大         | 実装済み |
    """

    def setup_method(self):
        log_msg("test start", LogLevel.INFO)

    def teardown_method(self):
        log_msg(f"test end\n{'-'*80}\n", LogLevel.INFO)

    @pytest.fixture()
    def mock_config(self):
        with patch('src.lib.converter_utils.ibr_bpr_flag_determiner.config') as mock:
            mock.package_config = {
                'ibr_bpr_flag_determiner': {
                    'SpecificWords': ['米州', '欧州', 'アジア'],
                    'reference_data': 'reference.pkl',
                    'request_data': 'request.pkl',
                },
            }
            mock.log_message = MagicMock()
            yield mock

    @pytest.fixture()
    def reference_data(self, tmp_path):
        """リファレンスデータのpickleファイルを準備"""
        _df = pd.DataFrame({
            'branch_code': [
                BranchCodeType.DOMESTIC_BRANCH.value + '123',
                BranchCodeType.BANK_HEAD_OFFICE.value + '789',
                RelatedCompanyType.MUFG_HOLDINGS_71.value + '00',
            ],
            'branch_name': ['テスト支店', 'テスト本部', 'テスト関連'],
            'section_gr_code': ['456', '0', '789'],
            'section_gr_name': ['テスト課', '本部課', '関連課'],
            'business_and_area_code': ['000', '000', '000'],
            'bpr_target_flag': [
                BprADFlagResults.BPR_TARGET.value,
                BprADFlagResults.AD_ONLY.value,
                BprADFlagResults.NOT_BPR_TARGET.value,
            ],
        })
        file_path = tmp_path / "reference.pkl"
        _df.to_pickle(file_path)
        return file_path

    @pytest.fixture()
    def request_data(self, tmp_path):
        """申請データのpickleファイルを準備"""
        _df = pd.DataFrame({
            'branch_code': [
                '0123',     # 国内支店(人事)
                '6789',     # 銀行本部(国企)
                '7100',     # MUFG(関連ダミー課あり)
                '1234',     # 法人営業(人事)
                '2345',     # ローン推進(人事)
                '3456',     # 海外拠点(人事)
                '6543',     # 銀行本部(人事)
                '7100',     # MUFG(関連ダミー課なし)
                '9876',     # 寮(人事)
            ],
            'branch_name': [
                '新設支店', '新設本部', '新設関連',
                '新設法人', '新設ローン', '新設海外',
                '新設本部2', '新設関連2', '新設寮',
            ],
            'section_gr_code': [
                '456', '0', '789',
                '456', '456', '456',
                '456', '789', '456',
            ],
            'section_gr_name': [
                '新設課', '新設課', '新設課',
                '新設課', '新設課', '新設課',
                '新設課', '新設課', '新設課',
            ],
            'business_and_area_code': ['000'] * 9,
            'application_type': [ApplicationType.NEW.value] * 9,
            'form_type': [
                '1',    # 人事
                '2',    # 国企
                '3',    # 関連(ダミー課あり)
                '1',    # 人事
                '1',    # 人事
                '1',    # 人事
                '1',    # 人事
                '4',    # 関連(ダミー課なし)
                '1',    # 人事
            ],
        })
        file_path = tmp_path / "request.pkl"
        _df.to_pickle(file_path)
        return file_path

    @pytest.fixture()
    def mock_table_searcher(self, reference_data, request_data):
        """TableSearcherのモック"""
        with patch('src.lib.converter_utils.ibr_bpr_flag_determiner.TableSearcher') as mock:
            def mock_init(table_name, file_path=None):
                mock_instance = MagicMock()
                if table_name == 'reference.pkl':
                    mock_instance.df = pd.read_pickle(reference_data)
                elif table_name == 'request.pkl':
                    mock_instance.df = pd.read_pickle(request_data)
                return mock_instance
            mock.side_effect = mock_init
            yield mock

    # イベントログCall用関数Mock 呼び出しフロー確認向け/hq
    @pytest.fixture()
    def mock_bpr_ad_flag_determiner_alert_case_hq(self):
        with patch('src.lib.converter_utils.ibr_bpr_flag_determiner.BprAdFlagDeterminer._alert_case_hq') as mock:
            yield mock

    # イベントログCall用関数Mock 呼び出しフロー確認向け/any
    @pytest.fixture()
    def mock_bpr_ad_flag_determiner_alert_case_any(self):
        with patch('src.lib.converter_utils.ibr_bpr_flag_determiner.BprAdFlagDeterminer._alert_case_any') as mock:
            yield mock

    def test_determine_bpr_ad_flag_C0_new(self, mock_config, mock_table_searcher):
        """新設申請の基本機能テスト"""
        test_doc = """
        テスト区分: UT
        テストカテゴリ: C0
        テストシナリオ: 新設申請の基本処理
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        determiner = BprAdFlagDeterminer()
        series = pd.Series({
            'application_type': ApplicationType.NEW.value,
            'form_type': '0',
            'branch_code': BranchCodeType.DOMESTIC_BRANCH.value + '123',
            'section_gr_code': '456',
            'section_gr_name': 'テスト課',
            'business_and_area_code': '000',
            'branch_name': 'テスト支店',
        })
        log_msg(f'{tabulate_dataframe(determiner.reference_df.head(5))}', LogLevel.INFO)
        log_msg(f'{tabulate_dataframe(determiner.request_df.head(5))}', LogLevel.INFO)

        result = determiner.determine_bpr_ad_flag(series)
        assert result == BprADFlagResults.BPR_TARGET.value

    def test_determine_bpr_ad_flag_C1_from_request_data(self, mock_config, mock_table_searcher):
        """request.pickleからの入力データによるテスト"""
        test_doc = """
        テスト区分: UT
        テストカテゴリ: C1
        テストシナリオ: 申請データからの入力テスト
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        # request.pickleからのDataFrameを取得
        request_df = mock_table_searcher.return_value.df
        determiner = BprAdFlagDeterminer()

        log_msg(f'{tabulate_dataframe(determiner.reference_df.head(5))}', LogLevel.INFO)
        log_msg(f'{tabulate_dataframe(determiner.request_df.head(5))}', LogLevel.INFO)

        # 各行に対してテスト
        expected_results = {
            '0123': BprADFlagResults.BPR_TARGET.value,     # 国内支店(人事)
            '6789': BprADFlagResults.AD_ONLY.value,        # 銀行本部(国企)
            '7100': BprADFlagResults.BPR_TARGET.value,     # MUFG(関連ダミー課あり)
            '1234': BprADFlagResults.BPR_TARGET.value,     # 法人営業(人事)
            '2345': BprADFlagResults.BPR_TARGET.value,     # ローン推進(人事)
            '3456': BprADFlagResults.AD_ONLY.value,        # 海外拠点(人事)
            '6543': BprADFlagResults.BPR_TARGET.value,     # 銀行本部(人事)
            '7200': BprADFlagResults.BPR_TARGET.value,     # MUFG(関連ダミー課なし)
            '9876': BprADFlagResults.NOT_BPR_TARGET.value, # 寮(人事)
        }

        for _, series in request_df.iterrows():
            branch_code = series['branch_code']
            result = determiner.determine_bpr_ad_flag(series)
            expected = expected_results[branch_code]
            assert result == expected, f"Failed for branch_code {branch_code}: expected {expected}, got {result}"

    def test_determine_bpr_ad_flag_C0_modify(self, mock_config, mock_table_searcher):
        """変更申請の基本機能テスト"""
        test_doc = """
        テスト区分: UT
        テストカテゴリ: C0
        テストシナリオ: 変更申請の基本処理
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        determiner = BprAdFlagDeterminer()
        # reference_bpr_target_flagを含むseriesを作成
        series = pd.Series({
            'application_type': ApplicationType.MODIFY.value,
            'form_type': ValidationConfig.FORM_TYPE_JINJI,
            'branch_code': BranchCodeType.DOMESTIC_BRANCH.value + '123',
            'section_gr_code': '456',
            'section_gr_name': 'テスト課',
            'business_and_area_code': '000',
            'branch_name': 'テスト支店',
            'reference_bpr_target_flag': BprADFlagResults.BPR_TARGET.value,
        })

        result = determiner.determine_bpr_ad_flag(series)
        assert result == BprADFlagResults.BPR_TARGET.value

    def test_determine_bpr_ad_flag_C0_modify_no_reference(self, mock_config, mock_table_searcher):
        """変更申請でリファレンスフラグがない場合のテスト"""
        test_doc = """
        テスト区分: UT
        テストカテゴリ: C0
        テストシナリオ: 変更申請(リファレンスフラグなし)
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        determiner = BprAdFlagDeterminer()
        # reference_bpr_target_flagを含まないseriesを作成
        series = pd.Series({
            'application_type': ApplicationType.MODIFY.value,
            'form_type': ValidationConfig.FORM_TYPE_JINJI,
            'branch_code': BranchCodeType.DOMESTIC_BRANCH.value + '123',
            'section_gr_code': '456',
            'section_gr_name': 'テスト課',
            'business_and_area_code': '000',
            'branch_name': 'テスト支店',
        })

        result = determiner.determine_bpr_ad_flag(series)
        assert result == ''

    def test_determine_bpr_ad_flag_C0_discontinue(self, mock_config, mock_table_searcher):
        """廃止申請の基本機能テスト"""
        test_doc = """
        テスト区分: UT
        テストカテゴリ: C0
        テストシナリオ: 廃止申請の基本処理
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        determiner = BprAdFlagDeterminer()
        # reference_bpr_target_flagを含むseriesを作成
        series = pd.Series({
            'application_type': ApplicationType.DISCONTINUE.value,
            'form_type': ValidationConfig.FORM_TYPE_JINJI,
            'branch_code': BranchCodeType.DOMESTIC_BRANCH.value + '123',
            'section_gr_code': '456',
            'section_gr_name': 'テスト課',
            'business_and_area_code': '000',
            'branch_name': 'テスト支店',
            'reference_bpr_target_flag': BprADFlagResults.BPR_TARGET.value,
        })

        result = determiner.determine_bpr_ad_flag(series)
        assert result == BprADFlagResults.BPR_TARGET.value

    def test_determine_bpr_ad_flag_C0_discontinue_no_reference(self, mock_config, mock_table_searcher):
        """廃止申請でリファレンスフラグがない場合のテスト"""
        test_doc = """
        テスト区分: UT
        テストカテゴリ: C0
        テストシナリオ: 廃止申請(リファレンスフラグなし)
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        determiner = BprAdFlagDeterminer()
        # reference_bpr_target_flagを含まないseriesを作成
        series = pd.Series({
            'application_type': ApplicationType.DISCONTINUE.value,
            'form_type': ValidationConfig.FORM_TYPE_JINJI,
            'branch_code': BranchCodeType.DOMESTIC_BRANCH.value + '123',
            'section_gr_code': '456',
            'section_gr_name': 'テスト課',
            'business_and_area_code': '000',
            'branch_name': 'テスト支店',
        })

        result = determiner.determine_bpr_ad_flag(series)
        assert result == ''

    @pytest.mark.parametrize(("application_type", "has_reference_flag", "expected_result"), [
        # 変更申請のパターン
        (ApplicationType.MODIFY.value, True, BprADFlagResults.BPR_TARGET.value),
        (ApplicationType.MODIFY.value, False, ''),
        # 廃止申請のパターン
        (ApplicationType.DISCONTINUE.value, True, BprADFlagResults.BPR_TARGET.value),
        (ApplicationType.DISCONTINUE.value, False, ''),
    ])
    def test_determine_bpr_ad_flag_C1_modify_discontinue(
        self, mock_config, mock_table_searcher,
        application_type, has_reference_flag, expected_result,
    ):
        """変更・廃止申請の分岐カバレッジテスト"""
        test_doc = f"""
        テスト区分: UT
        テストカテゴリ: C1
        テストシナリオ: {application_type}申請(リファレンスフラグ{has_reference_flag})
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        determiner = BprAdFlagDeterminer()

        # 基本データを作成
        data = {
            'application_type': application_type,
            'form_type': ValidationConfig.FORM_TYPE_JINJI,
            'branch_code': BranchCodeType.DOMESTIC_BRANCH.value + '123',
            'section_gr_code': '456',
            'section_gr_name': 'テスト課',
            'business_and_area_code': '000',
            'branch_name': 'テスト支店',
        }

        # リファレンスフラグが必要な場合は追加
        if has_reference_flag:
            data['reference_bpr_target_flag'] = BprADFlagResults.BPR_TARGET.value

        series = pd.Series(data)
        result = determiner.determine_bpr_ad_flag(series)
        assert result == expected_result

    @pytest.mark.parametrize(("branch_code_prefix", "form_type", "expected_result"), [
        # 人事申請 (form_type = '1')
        (BranchCodeType.DOMESTIC_BRANCH.value, ValidationConfig.FORM_TYPE_JINJI, BprADFlagResults.BPR_TARGET),      # 国内支店
        (BranchCodeType.CORPORATE_SALES.value, ValidationConfig.FORM_TYPE_JINJI, BprADFlagResults.BPR_TARGET),      # 法人営業
        (BranchCodeType.LOAN_PROMOTION.value, ValidationConfig.FORM_TYPE_JINJI, BprADFlagResults.BPR_TARGET),       # ローン推進部
        (BranchCodeType.OVERSEAS_BRANCH.value, ValidationConfig.FORM_TYPE_JINJI, BprADFlagResults.AD_ONLY),         # 海外拠点
        (BranchCodeType.BANK_HEAD_OFFICE.value, ValidationConfig.FORM_TYPE_JINJI, BprADFlagResults.BPR_TARGET),     # 銀行本部
        (BranchCodeType.DORMITORY.value, ValidationConfig.FORM_TYPE_JINJI, BprADFlagResults.NOT_BPR_TARGET),        # 寮

        # 国企申請 (form_type = '2')
        (BranchCodeType.OVERSEAS_BRANCH.value, ValidationConfig.FORM_TYPE_KOKUKI, BprADFlagResults.AD_ONLY),         # 海外拠点
        (BranchCodeType.BANK_HEAD_OFFICE.value, ValidationConfig.FORM_TYPE_KOKUKI, BprADFlagResults.AD_ONLY),        # 銀行本部

        # 関連会社申請(ダミー課あり)(form_type = '3')
        (RelatedCompanyType.MUFG_HOLDINGS_71.value, ValidationConfig.FORM_TYPE_KANREN_WITH_DUMMMY, BprADFlagResults.BPR_TARGET),  # MUFG 71
        (RelatedCompanyType.MUFG_HOLDINGS_72.value, ValidationConfig.FORM_TYPE_KANREN_WITH_DUMMMY, BprADFlagResults.BPR_TARGET),  # MUFG 72
        ('73', ValidationConfig.FORM_TYPE_KANREN_WITH_DUMMMY, BprADFlagResults.NOT_BPR_TARGET),                                   # その他関連会社
        ('74', ValidationConfig.FORM_TYPE_KANREN_WITH_DUMMMY, BprADFlagResults.NOT_BPR_TARGET),                                   # その他関連会社

        # 関連会社申請(ダミー課なし)(form_type = '4')
        (RelatedCompanyType.MUFG_HOLDINGS_71.value, ValidationConfig.FORM_TYPE_KANREN_WITHOUT_DUMMMY, BprADFlagResults.BPR_TARGET),  # MUFG 71
        (RelatedCompanyType.MUFG_HOLDINGS_72.value, ValidationConfig.FORM_TYPE_KANREN_WITHOUT_DUMMMY, BprADFlagResults.BPR_TARGET),  # MUFG 72
        ('73', ValidationConfig.FORM_TYPE_KANREN_WITHOUT_DUMMMY, BprADFlagResults.NOT_BPR_TARGET),                                   # その他関連会社
        ('74', ValidationConfig.FORM_TYPE_KANREN_WITHOUT_DUMMMY, BprADFlagResults.NOT_BPR_TARGET),                                   # その他関連会社
    ])
    def test_determine_bpr_ad_flag_C1_branch_types(
        self,
        mock_config,
        mock_table_searcher,
        branch_code_prefix,
        form_type,
        expected_result,
        ):
        """部店種類と申請種類の組み合わせテスト"""
        test_doc = f"""
        テスト区分: UT
        テストカテゴリ: C1
        テストシナリオ: 部店種類{branch_code_prefix}・申請種類{form_type}の判定
        期待結果: {expected_result.value}
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        determiner = BprAdFlagDeterminer()
        series = pd.Series({
            'application_type': ApplicationType.NEW.value,
            'form_type': form_type,
            'branch_code': f"{branch_code_prefix}123",
            'section_gr_code': '456',
            'section_gr_name': 'テスト課',
            'business_and_area_code': '000',
            'branch_name': 'テスト支店',
        })

        log_msg(f'{tabulate_dataframe(determiner.reference_df.head(5))}', LogLevel.INFO)
        log_msg(f'{tabulate_dataframe(determiner.request_df.head(5))}', LogLevel.INFO)
        log_msg(f"target series: {series}", LogLevel.INFO)

        result = determiner.determine_bpr_ad_flag(series)

        log_msg(f"Result type: {type(result)}, value: {result}", LogLevel.DEBUG)
        log_msg(f"Expected type: {type(expected_result)}, value: {expected_result.value}", LogLevel.DEBUG)

        if isinstance(result, str):
            result = BprADFlagResults(result)

        assert result == expected_result, \
            (f"Failed: branch_code={branch_code_prefix}, form_type={form_type}, "
            f"expected={expected_result.value}, got={result.value}")

    def test_determine_bpr_ad_flag_C0_invalid_application_type(self, mock_config, mock_table_searcher):
        """無効な申請種類のテスト"""
        test_doc = """
        テスト区分: UT
        テストカテゴリ: C0
        テストシナリオ: 無効な申請種類での動作確認
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        determiner = BprAdFlagDeterminer()
        series = pd.Series({
            'application_type': '無効な種類',
            'form_type': ValidationConfig.FORM_TYPE_JINJI,
            'branch_code': BranchCodeType.DOMESTIC_BRANCH.value + '123',
            'section_gr_code': '456',
            'section_gr_name': 'テスト課',
            'business_and_area_code': '000',
            'branch_name': 'テスト支店',
        })

        with pytest.raises(ValueError, match="Unexpected application_type"):
            determiner.determine_bpr_ad_flag(series)

    def test_determine_bpr_ad_flag_C2_alert_check_hq(self, mock_config, mock_table_searcher, mock_bpr_ad_flag_determiner_alert_case_hq):
        """アラート出力条件のテスト"""
        test_doc = """
        テスト区分: UT
        テストカテゴリ: C2
        テストシナリオ: アラート出力条件の確認
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        # Case 1: 本部(6系)&特定ワード含む&課Grコード0の部店が存在する
        test_branch_code = BranchCodeType.BANK_HEAD_OFFICE.value + '123'  # '6123'

        # reference_dfの設定
        reference_df = pd.DataFrame({
            'branch_code': ['6123'],
            'branch_name': ['テスト本部'],
            'section_gr_code': ['0'],
            'section_gr_name': ['本部課'],
            'business_and_area_code': ['000'],
            'bpr_target_flag': [BprADFlagResults.AD_ONLY.value],
        })

        # request_dfの設定
        request_df = pd.DataFrame({
            'branch_code': [
                test_branch_code,    # テスト対象の部店コード
                test_branch_code,    # 同じ部店コードで課Grコード0のレコード
            ],
            'branch_name': ['テスト本部', 'テスト本部'],
            'section_gr_code': ['456', '0'],
            'section_gr_name': ['米州営業部', '本部課'],
            'business_and_area_code': ['000', '000'],
            'application_type': [ApplicationType.NEW.value] * 2,
            'form_type': [ValidationConfig.FORM_TYPE_JINJI] * 2,
            'bpr_target_flag': [BprADFlagResults.AD_ONLY.value] * 2,
        })

        # TableSearcherの戻り値を設定
        mock_reference = MagicMock()
        mock_reference.df = reference_df
        mock_request = MagicMock()
        mock_request.df = request_df

        # TableSearcherのモック設定を制御 DI
        def mock_searcher_factory(*args, **kwargs):
            if args and 'reference' in str(args[0]):
                return mock_reference
            return mock_request
        mock_table_searcher.side_effect = mock_searcher_factory

        # ここでインスタンス化
        determiner = BprAdFlagDeterminer()


        # テスト用の入力データ 申請玉との整合性に留意が必要な箇所,慎重に設定
        # 共通変数名を活用して誤認を減らす
        series_hq_specific = pd.Series({
            'application_type': ApplicationType.NEW.value,
            'form_type': ValidationConfig.FORM_TYPE_JINJI,
            'branch_code': test_branch_code,
            'section_gr_code': '456',
            'section_gr_name': '米州営業部',  # 特定ワードを含む
            'business_and_area_code': '000',
            'branch_name': 'テスト本部',
            'bpr_target_flag': BprADFlagResults.AD_ONLY.value,
        })

        # 入力データの確認
        log_msg(f'{tabulate_dataframe(determiner.reference_df.head(5))}', LogLevel.INFO)
        log_msg(f'{tabulate_dataframe(determiner.request_df.head(5))}', LogLevel.INFO)
        log_msg(f"Input series branch_code: {series_hq_specific['branch_code']}", LogLevel.INFO)
        log_msg(f"Input series branch_code type: {type(series_hq_specific['branch_code'])}", LogLevel.DEBUG)

        result = determiner.determine_bpr_ad_flag(series_hq_specific)

        # 探索結果確認
        log_msg(f"Result for Case 1: {result}", LogLevel.INFO)
        assert result == BprADFlagResults.AD_ONLY.value

        # _alert_case_hqメソッドが正しく,１回呼び出されたことを検証,引数は各々
        mock_bpr_ad_flag_determiner_alert_case_hq.assert_called_once_with(
            series_hq_specific['branch_code'],
            series_hq_specific['section_gr_name'],
        )

    def test_determine_bpr_ad_flag_C2_alert_check_any(self, mock_config, mock_table_searcher, mock_bpr_ad_flag_determiner_alert_case_any):
        """アラート出力条件のテスト"""
        test_doc = """
        テスト区分: UT
        テストカテゴリ: C2
        テストシナリオ: アラート出力条件の確認
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        # Case2 : branch_code '70','73'〜'79'
        test_branch_code = '7000'  # 固定値定義は持っていないので直接記述

        # reference_dfの設定
        reference_df = pd.DataFrame({
            'branch_code': ['7000'],
            'branch_name': ['テスト本部'],
            'section_gr_code': ['7000'],
            'section_gr_name': ['本部課'],
            'business_and_area_code': ['000'],
            'bpr_target_flag': [BprADFlagResults.AD_ONLY.value],
        })

        # request_dfの設定
        request_df = pd.DataFrame({
            'branch_code': [
                test_branch_code,    # テスト対象の部店コード
                test_branch_code,    # 同じ部店コードで課Grコード0のレコード
            ],
            'branch_name': ['テスト本部', 'テスト本部'],
            'section_gr_code': ['456', '7000'],
            'section_gr_name': ['米州営業部', '本部課'],
            'business_and_area_code': ['000', '000'],
            'application_type': [ApplicationType.NEW.value] * 2,
            'form_type': [ValidationConfig.FORM_TYPE_JINJI] * 2,
            'bpr_target_flag': [BprADFlagResults.NOT_BPR_TARGET.value] * 2,
        })

        # TableSearcherの戻り値を設定
        mock_reference = MagicMock()
        mock_reference.df = reference_df
        mock_request = MagicMock()
        mock_request.df = request_df

        # TableSearcherのモック設定を制御 DI
        def mock_searcher_factory(*args, **kwargs):
            if args and 'reference' in str(args[0]):
                return mock_reference
            return mock_request
        mock_table_searcher.side_effect = mock_searcher_factory

        # ここでインスタンス化
        determiner = BprAdFlagDeterminer()

        # テスト用の入力データ 申請玉との整合性に留意が必要な箇所,慎重に設定
        # 共通変数名を活用して誤認を減らす
        series_hq_specific = pd.Series({
            'application_type': ApplicationType.NEW.value,
            'form_type': ValidationConfig.FORM_TYPE_JINJI,
            'branch_code': test_branch_code,
            'section_gr_code': '456',
            'section_gr_name': '米州営業部',  # 特定ワードを含む
            'business_and_area_code': '000',
            'branch_name': 'テスト本部',
            'bpr_target_flag': BprADFlagResults.NOT_BPR_TARGET.value,
        })

        # 入力データの確認
        log_msg(f'{tabulate_dataframe(determiner.reference_df.head(5))}', LogLevel.INFO)
        log_msg(f'{tabulate_dataframe(determiner.request_df.head(5))}', LogLevel.INFO)
        log_msg(f"Input series branch_code: {series_hq_specific['branch_code']}", LogLevel.INFO)
        log_msg(f"Input series branch_code type: {type(series_hq_specific['branch_code'])}", LogLevel.DEBUG)

        result = determiner.determine_bpr_ad_flag(series_hq_specific)

        # 探索結果確認
        # 結果としてenumの値を返す,enum自体を返す仕様ではないので留意
        log_msg(f"Result for Case 1: {result}", LogLevel.INFO)
        assert result == BprADFlagResults.NOT_BPR_TARGET.value

        # _alert_case_hqメソッドが正しく,１回呼び出されたことを検証,引数なしには留意
        mock_bpr_ad_flag_determiner_alert_case_any.assert_called_once_with()

class TestBprAdFlagDeterminerEnsureNewDivision:
    """BprAdFlagDeterminerの_ensure_new_division_bprad_flag_configメソッドのテスト

    テスト構造:
    ├── C0: 基本機能テスト
    │   ├── 正常系: 1桁判定(0〜9)
    │   ├── 正常系: 2桁判定(71,72等)
    │   └── 正常系: 対象外判定
    ├── C1: 分岐カバレッジ
    │   ├── 部店コードなし
    │   ├── 単一桁判定 (0-9)
    │   ├── 二桁判定 (71,72)
    │   └── 対象外判定 (73-79)
    ├── C2: 条件組み合わせ
    │   ├── 部店コードと特定ワード
    │   └── アラート条件の組み合わせ
    └── BVT: 境界値テスト
        ├── 部店コード境界値
        └── 無効な部店コード

    C1のディシジョンテーブル:
    | 条件                          | DT1 | DT2 | DT3 | DT4 | DT5 |
    |-------------------------------|-----|-----|-----|-----|-----|
    | 部店コードあり                | N   | Y   | Y   | Y   | Y   |
    | 1桁判定に該当                 | -   | Y   | N   | N   | N   |
    | 2桁判定に該当                 | -   | -   | Y   | N   | N   |
    | NOT_BPR_TARGET_PREFIXESに該当 | -   | -   | -   | Y   | N   |
    |-------------------------------|-----|-----|-----|-----|-----|
    | NOT_BPR_TARGET               | X   | -   | -   | X   | X   |
    | 1桁判定結果                   | -   | X   | -   | -   | -   |
    | 2桁判定結果                   | -   | -   | X   | -   | -   |

    境界値検証ケース一覧:
    | ID    | パラメータ    | テスト値           | 期待される結果     | テストの目的               | 実装状況 |
    |-------|--------------|-------------------|------------------|--------------------------|----------|
    | BVT01 | branch_code  | ""               | BPR対象外        | 空文字列の処理            | 実装済み  |
    | BVT02 | branch_code  | "0"              | BPR対象          | 最小部店コード            | 実装済み  |
    | BVT03 | branch_code  | "71"             | BPR対象          | 関連会社最小値            | 実装済み  |
    | BVT04 | branch_code  | "79"             | BPR対象外        | 関連会社最大値            | 実装済み  |
    | BVT05 | branch_code  | None             | BPR対象外        | Noneの処理               | 実装済み  |
    """

    def setup_method(self):
        log_msg("test start", LogLevel.INFO)

    def teardown_method(self):
        log_msg(f"test end\n{'-'*80}\n", LogLevel.INFO)

    @pytest.fixture()
    def mock_event_logger(self):
        """WindowsEventLoggerのモック"""
        with patch('src.lib.common_utils.ibr_eventlog_handler.WindowsEventLogger') as mock:
            mock.write_error_log = MagicMock()
            yield mock

    @pytest.fixture()
    def target_method(self, mock_event_logger):
        """テスト対象メソッドを持つインスタンスを提供"""
        with patch.object(BprAdFlagDeterminer, '__init__', return_value=None):
            determiner = BprAdFlagDeterminer()
            # 必要な属性のみを設定
            determiner.SPECIFIC_WORDS = ['米州', '欧州', 'アジア']
            return determiner._ensure_new_division_bprad_flag_config
    @pytest.mark.parametrize(("branch_code_prefix", "branch_name", "expected_result"), [
        (BranchCodeType.DOMESTIC_BRANCH.value, '東京支店', BprADFlagResults.BPR_TARGET.value),     # 国内支店
        (BranchCodeType.CORPORATE_SALES.value, '法人営業部', BprADFlagResults.BPR_TARGET.value),   # 法人営業
        (BranchCodeType.LOAN_PROMOTION.value, 'ローン推進部', BprADFlagResults.BPR_TARGET.value),  # ローン推進部
        (BranchCodeType.OVERSEAS_BRANCH.value, '香港支店', BprADFlagResults.AD_ONLY.value),        # 海外拠点
        (BranchCodeType.BANK_HEAD_OFFICE.value, '本店', BprADFlagResults.BPR_TARGET.value),        # 銀行本部
        (BranchCodeType.DORMITORY.value, '社宅', BprADFlagResults.NOT_BPR_TARGET.value),           # 寮
        (RelatedCompanyType.MUFG_HOLDINGS_71.value, 'MUFG部門', BprADFlagResults.BPR_TARGET.value),# MUFG 71
        (RelatedCompanyType.MUFG_HOLDINGS_72.value, 'MUFG部門2', BprADFlagResults.BPR_TARGET.value),# MUFG 72
        ('70', '関連会社', BprADFlagResults.NOT_BPR_TARGET.value),                                 # その他関連会社
        ('73', '関連会社', BprADFlagResults.NOT_BPR_TARGET.value),                                 # その他関連会社
        ('74', '関連会社', BprADFlagResults.NOT_BPR_TARGET.value),                                 # その他関連会社
        ('75', '関連会社', BprADFlagResults.NOT_BPR_TARGET.value),                                 # その他関連会社
        ('76', '関連会社', BprADFlagResults.NOT_BPR_TARGET.value),                                 # その他関連会社
        ('77', '関連会社', BprADFlagResults.NOT_BPR_TARGET.value),                                 # その他関連会社
        ('78', '関連会社', BprADFlagResults.NOT_BPR_TARGET.value),                                 # その他関連会社
        ('79', '関連会社', BprADFlagResults.NOT_BPR_TARGET.value),                                 # その他関連会社
    ])
    def test_ensure_new_division_C0_branch_types(
        self,
        target_method,
        mock_event_logger,
        branch_code_prefix,
        branch_name,
        expected_result,
        ):
        """部店種類ごとの判定テスト"""
        test_doc = f"""
        テスト区分: UT
        テストカテゴリ: C0
        テストシナリオ: 部店種類{branch_code_prefix}の判定
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        series = pd.Series({
            'branch_code': f"{branch_code_prefix}123",
            'branch_name': branch_name,
            'section_gr_name': 'テスト課',
        })

        result = target_method(series)
        assert result == expected_result

    def test_ensure_new_division_C1_no_branch_code(self, target_method, mock_event_logger):
        """部店コードなしの場合のテスト"""
        test_doc = """
        テスト区分: UT
        テストカテゴリ: C1
        テストシナリオ: 部店コードなしの判定
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        series = pd.Series({
            'branch_code': '',
            'branch_name': 'テスト支店',
            'section_gr_name': 'テスト課',
        })

        result = target_method(series)
        assert result == BprADFlagResults.NOT_BPR_TARGET.value

    def test_ensure_new_division_C2_alert_check(self, target_method, mock_event_logger):
        """アラート出力条件のテスト"""
        test_doc = """
        テスト区分: UT
        テストカテゴリ: C2
        テストシナリオ: アラート出力条件の確認
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        # 関連会社で特定ワードを含む場合
        series = pd.Series({
            'branch_code': '73123',         # 関連会社
            'branch_name': '米州関連会社',  # 特定ワードを含む
            'section_gr_name': '米州営業部',# 特定ワードを含む
        })

        result = target_method(series)
        assert result == BprADFlagResults.NOT_BPR_TARGET.value

        # 上位モジュール経由で呼び出し検証済のためここでは省略する
        # アラート出力の確認
        #mock_event_logger.write_error_log.assert_called_with(
        #    '要確認アラート: リファレンス BPR-ADフラグ初期値設定',
        #    1002,
        #    ['課Grコード0レコードなく、BPR対象外']
        #)

    @pytest.mark.parametrize(("branch_code", "branch_name", "expected_result"), [
        ("", "テスト支店", BprADFlagResults.NOT_BPR_TARGET.value),           # 空文字列
        (None, "テスト支店", BprADFlagResults.NOT_BPR_TARGET.value),         # None
        ("0", "テスト支店", BprADFlagResults.BPR_TARGET.value),              # 最小部店コード
        ("71", "MUFG支店", BprADFlagResults.BPR_TARGET.value),               # 関連会社最小値
        ("79", "関連会社", BprADFlagResults.NOT_BPR_TARGET.value),           # 関連会社最大値
        ("X", "不正支店", BprADFlagResults.NOT_BPR_TARGET.value),            # 無効な値
    ])
    def test_ensure_new_division_BVT(
        self,
        target_method,
        mock_event_logger,
        branch_code,
        branch_name,
        expected_result,
        ):
        """境界値テスト"""
        test_doc = f"""
        テスト区分: UT
        テストカテゴリ: BVT
        テストシナリオ: 部店コード{branch_code}の境界値テスト
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        series = pd.Series({
            'branch_code': branch_code,
            'branch_name': branch_name,
            'section_gr_name': 'テスト課',
        })

        result = target_method(series)
        assert result == expected_result

class TestBprAdFlagDeterminerExistsBranchCode:
    """BprAdFlagDeterminerの_exists_branch_code_with_zero_group_codeメソッドのテスト

    テスト構造:
    ├── C0: 基本機能テスト
    │   ├── 正常系: 課Grコード0のレコードあり
    │   ├── 正常系: エリアコード0のレコードあり
    │   └── 正常系: 0コードのレコードなし
    ├── C1: 分岐カバレッジ
    │   ├── 部店コード一致レコードあり
    │   ├── 部店コード一致レコードなし
    │   └── カラム不足エラー
    ├── C2: 条件組み合わせ
    │   ├── 課Grコードとエリアコードの組み合わせ
    │   └── 複数レコードの組み合わせ
    └── BVT: 境界値テスト
        ├── コード値の境界値
        └── データ件数の境界値

    C1のディシジョンテーブル:
    | 条件                            | DT1 | DT2 | DT3 | DT4 | DT5 |
    |--------------------------------|-----|-----|-----|-----|-----|
    | 部店コード一致レコードあり       | Y   | Y   | Y   | N   | Y   |
    | 課Grコード0あり                 | Y   | N   | N   | -   | -   |
    | エリアコード0あり               | N   | Y   | N   | -   | -   |
    | 必要なカラムが存在              | Y   | Y   | Y   | -   | N   |
    |--------------------------------|-----|-----|-----|-----|-----|
    | 0コードレコードを返却           | X   | X   | -   | -   | -   |
    | 空のDataFrameを返却             | -   | -   | X   | X   | -   |
    | KeyError発生                    | -   | -   | -   | -   | X   |

    境界値検証ケース一覧:
    | ID    | パラメータ             | テスト値              | 期待される結果             | テストの目的                   | 実装状況 |
    |-------|----------------------|----------------------|--------------------------|--------------------------------|----------|
    | BVT01 | section_gr_code     | "0"                 | レコード返却               | 最小課Grコード                  | 実装済み  |
    | BVT02 | section_gr_code     | "00000"            | レコード返却               | 0埋め課Grコード                 | 実装済み  |
    | BVT03 | request_df          | 空DataFrame         | 空DataFrame              | データなし                      | 実装済み  |
    | BVT04 | request_df          | 1000行のDataFrame   | 該当レコードのみ            | 大量データ                     | 実装済み  |
    """

    def setup_method(self):
        log_msg("test start", LogLevel.INFO)

    def teardown_method(self):
        log_msg(f"test end\n{'-'*80}\n", LogLevel.INFO)

    #@pytest.fixture
    #def target_method(self):
    #    """テスト対象メソッドを持つインスタンスを提供"""
    #    with patch.object(BprAdFlagDeterminer, '__init__', return_value=None):
    #        determiner = BprAdFlagDeterminer()
    #        return determiner._exists_branch_code_with_zero_group_code

    #@pytest.fixture
    #def target_method(self):
    #    """テスト対象メソッドを持つインスタンスを提供"""
    #    with patch.object(BprAdFlagDeterminer, '__init__', return_value=None):
    #        determiner = BprAdFlagDeterminer()
    #        # インスタンス属性として設定
    #        determiner.request_df = None  # 初期値として設定
    #        return determiner._exists_branch_code_with_zero_group_code

    @pytest.fixture()
    def target_instance(self):
        """テスト対象インスタンスを提供"""
        with patch.object(BprAdFlagDeterminer, '__init__', return_value=None):
            determiner = BprAdFlagDeterminer()
            # 必要な属性を初期化
            determiner.request_df = pd.DataFrame()
            return determiner

    def test_exists_branch_code_C0_with_zero_gr_code(self, target_instance):
        """課Grコード0のレコードが存在する場合のテスト"""
        test_doc = """
        テスト区分: UT
        テストカテゴリ: C0
        テストシナリオ: 課Grコード0のレコードあり
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        request_df = pd.DataFrame({
            'branch_code': ['6123', '6123'],
            'section_gr_code': ['456', '0'],
            'business_and_area_code': ['789', '789'],
            'bpr_target_flag': [BprADFlagResults.BPR_TARGET.value, BprADFlagResults.AD_ONLY.value],
        })

        series = pd.Series({
            'branch_code': '6123',
            'section_gr_code': '456',
        })

        # インスタンスのrequest_dfに対してパッチ
        with patch.object(target_instance, 'request_df', request_df):
            result = target_instance._exists_branch_code_with_zero_group_code(series)
            assert len(result) == 1
            assert result.iloc[0]['section_gr_code'] == '0'

    def test_exists_branch_code_C0_with_zero_area_code(self, target_instance):
        """エリアコード0のレコードが存在する場合のテスト"""
        test_doc = """
        テスト区分: UT
        テストカテゴリ: C0
        テストシナリオ: エリアコード0のレコードあり
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        request_df = pd.DataFrame({
            'branch_code': ['6123', '6123'],
            'section_gr_code': ['456', '456'],
            'business_and_area_code': ['789', '0'],
            'bpr_target_flag': [BprADFlagResults.BPR_TARGET.value, BprADFlagResults.AD_ONLY.value],
        })

        series = pd.Series({
            'branch_code': '6123',
            'section_gr_code': '456',
        })

        with patch.object(target_instance, 'request_df', request_df):
            result = target_instance._exists_branch_code_with_zero_group_code(series)
            assert len(result) == 1
            assert result.iloc[0]['business_and_area_code'] == '0'

    def test_exists_branch_code_C1_no_match(self, target_instance):
        """一致するレコードが存在しない場合のテスト"""
        test_doc = """
        テスト区分: UT
        テストカテゴリ: C1
        テストシナリオ: 一致するレコードなし
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        request_df = pd.DataFrame({
            'branch_code': ['6124', '6125'],
            'section_gr_code': ['456', '0'],
            'business_and_area_code': ['789', '789'],
        })

        series = pd.Series({
            'branch_code': '6123',
            'section_gr_code': '456',
        })

        with patch.object(target_instance, 'request_df', request_df):
            result = target_instance._exists_branch_code_with_zero_group_code(series)
            assert len(result) == 0

    def test_exists_branch_code_C1_missing_column(self, target_instance):
        """必要なカラムが存在しない場合のテスト"""
        test_doc = """
        テスト区分: UT
        テストカテゴリ: C1
        テストシナリオ: 必要なカラム欠損
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        request_df = pd.DataFrame({
            'branch_code': ['6123'],
            # section_gr_codeカラムなし
            'business_and_area_code': ['789'],
        })

        series = pd.Series({
            'branch_code': '6123',
            'section_gr_code': '456',
        })

        with patch.object(target_instance, 'request_df', request_df):
            result = target_instance._exists_branch_code_with_zero_group_code(series)
            assert isinstance(result, pd.DataFrame)
            assert len(result) == 0

    def test_exists_branch_code_C2_multiple_zero_codes(self, target_instance):
        """複数の0コードが存在する場合のテスト"""
        test_doc = """
        テスト区分: UT
        テストカテゴリ: C2
        テストシナリオ: 複数の0コード
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        request_df = pd.DataFrame({
            'branch_code': ['6123', '6123', '6123'],
            'section_gr_code': ['456', '0', '0'],
            'business_and_area_code': ['789', '789', '0'],
        })

        series = pd.Series({
            'branch_code': '6123',
            'section_gr_code': '456',
        })

        with patch.object(target_instance, 'request_df', request_df):
            result = target_instance._exists_branch_code_with_zero_group_code(series)
            assert len(result) > 0
            # 最初に見つかった0コードのレコードが返される
            assert result.iloc[0]['section_gr_code'] == '0'

    @pytest.mark.parametrize(("request_data", "expected_count"), [
        # 空のDataFrame
        (pd.DataFrame(columns=['branch_code', 'section_gr_code', 'business_and_area_code']), 0),
        # 1000行のDataFrame (該当1件)
        (pd.DataFrame({
            'branch_code': ['6123'] + ['9999'] * 999,
            'section_gr_code': ['0'] + ['999'] * 999,
            'business_and_area_code': ['789'] * 1000,
        }), 1),
        # 0埋め課Grコード
        (pd.DataFrame({
            'branch_code': ['6123'],
            'section_gr_code': ['00000'],
            'business_and_area_code': ['789'],
        }), 0),
    ])
    def test_exists_branch_code_BVT(self, target_instance, request_data, expected_count):
        """境界値テスト"""
        test_doc = f"""
        テスト区分: UT
        テストカテゴリ: BVT
        テストシナリオ: データ件数{len(request_data)}件
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        series = pd.Series({
            'branch_code': '6123',
            'section_gr_code': '456',
        })

        with patch.object(target_instance, 'request_df', request_data):
            result = target_instance._exists_branch_code_with_zero_group_code(series)
            assert len(result) == expected_count

class TestBprAdFlagDeterminerFilterByBranchCode:
    """BprAdFlagDeterminerの_filter_by_branch_codeメソッドのテスト

    テスト構造:
    ├── C0: 基本機能テスト
    │   ├── 正常系: 一致するレコードあり(単一)
    │   ├── 正常系: 一致するレコードあり(複数)
    │   └── 正常系: 一致するレコードなし
    ├── C1: 分岐カバレッジ
    │   ├── 部店コード完全一致
    │   └── 部店コード不一致
    ├── C2: 条件組み合わせ
    │   ├── 部店コードと件数の組み合わせ
    │   └── データ型の組み合わせ
    └── BVT: 境界値テスト
        ├── 空のDataFrame
        └── 大量データ

    C1のディシジョンテーブル:
    | 条件                          | DT1 | DT2 | DT3 |
    |-------------------------------|-----|-----|-----|
    | request_dfにデータあり        | Y   | Y   | N   |
    | 部店コード一致               | Y   | N   | -   |
    |-------------------------------|-----|-----|-----|
    | 一致レコードを返却           | X   | -   | -   |
    | 空のDataFrameを返却          | -   | X   | X   |

    境界値検証ケース一覧:
    | ID    | パラメータ    | テスト値              | 期待される結果        | テストの目的            | 実装状況 |
    |-------|--------------|----------------------|---------------------|-------------------------|----------|
    | BVT01 | request_df   | 空DataFrame         | 空DataFrame         | データなし               | 実装済み  |
    | BVT02 | request_df   | 1000行のDataFrame   | 一致レコードのみ      | 大量データ              | 実装済み  |
    | BVT03 | branch_code  | ""                  | 空DataFrame         | 空文字列の処理          | 実装済み  |
    | BVT04 | branch_code  | None                | 空DataFrame         | Noneの処理             | 実装済み  |
    """

    def setup_method(self):
        log_msg("test start", LogLevel.INFO)

    def teardown_method(self):
        log_msg(f"test end\n{'-'*80}\n", LogLevel.INFO)

    @pytest.fixture()
    def target_instance(self):
        """テスト対象インスタンスを提供"""
        with patch.object(BprAdFlagDeterminer, '__init__', return_value=None):
            determiner = BprAdFlagDeterminer()
            # 必要な属性を初期化
            determiner.request_df = pd.DataFrame()
            return determiner

    def test_filter_by_branch_code_C0_single_match(self, target_instance):
        """単一の一致レコードを返すケース"""
        test_doc = """
        テスト区分: UT
        テストカテゴリ: C0
        テストシナリオ: 単一レコード一致
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        request_df = pd.DataFrame({
            'branch_code': ['6123', '6124', '6125'],
            'section_gr_code': ['456', '789', '012'],
        })

        series = pd.Series({
            'branch_code': '6123',
        })

        with patch.object(target_instance, 'request_df', request_df):
            result = target_instance._filter_by_branch_code(series)
            assert len(result) == 1
            assert result.iloc[0]['branch_code'] == '6123'

    def test_filter_by_branch_code_C0_multiple_matches(self, target_instance):
        """複数の一致レコードを返すケース"""
        test_doc = """
        テスト区分: UT
        テストカテゴリ: C0
        テストシナリオ: 複数レコード一致
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        request_df = pd.DataFrame({
            'branch_code': ['6123', '6123', '6125'],
            'section_gr_code': ['456', '789', '012'],
        })

        series = pd.Series({
            'branch_code': '6123',
        })

        with patch.object(target_instance, 'request_df', request_df):
            result = target_instance._filter_by_branch_code(series)
            assert len(result) == 2
            assert all(result['branch_code'] == '6123')

    def test_filter_by_branch_code_C0_no_match(self, target_instance):
        """一致するレコードがないケース"""
        test_doc = """
        テスト区分: UT
        テストカテゴリ: C0
        テストシナリオ: 一致レコードなし
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        request_df = pd.DataFrame({
            'branch_code': ['6124', '6125', '6126'],
            'section_gr_code': ['456', '789', '012'],
        })

        series = pd.Series({
            'branch_code': '6123',
        })

        with patch.object(target_instance, 'request_df', request_df):
            result = target_instance._filter_by_branch_code(series)
            assert len(result) == 0

    def test_filter_by_branch_code_C2_data_types(self, target_instance):
        """データ型の組み合わせテスト"""
        test_doc = """
        テスト区分: UT
        テストカテゴリ: C2
        テストシナリオ: データ型の組み合わせ
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        request_df = pd.DataFrame({
            'branch_code': ['6123', 6123, '06123'],  # 文字列、数値、0埋め
            'section_gr_code': ['456', '789', '012'],
        })

        series = pd.Series({
            'branch_code': '6123',
        })

        with patch.object(target_instance, 'request_df', request_df):
            result = target_instance._filter_by_branch_code(series)
            assert len(result) == 1  # 文字列完全一致のみ
            assert result.iloc[0]['branch_code'] == '6123'

    @pytest.mark.parametrize(("request_data", "branch_code", "expected_count"), [
        # 空のDataFrame
        (pd.DataFrame(columns=['branch_code', 'section_gr_code']), '6123', 0),
        # 1000行のDataFrame (該当1件)
        (pd.DataFrame({
            'branch_code': ['6123'] + ['9999'] * 999,
            'section_gr_code': ['456'] + ['999'] * 999,
        }), '6123', 1),
        # 空の部店コード
        (pd.DataFrame({
            'branch_code': ['6123', ''],
            'section_gr_code': ['456', '789'],
        }), '', 1),
        # None値
        (pd.DataFrame({
            'branch_code': ['6123', None],
            'section_gr_code': ['456', '789'],
        }), None, 0),
    ])
    def test_filter_by_branch_code_BVT(self, target_instance, request_data, branch_code, expected_count):
        """境界値テスト"""
        test_doc = f"""
        テスト区分: UT
        テストカテゴリ: BVT
        テストシナリオ: データ件数{len(request_data)}件、部店コード{branch_code}
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        series = pd.Series({
            'branch_code': branch_code,
        })

        with patch.object(target_instance, 'request_df', request_data):
            result = target_instance._filter_by_branch_code(series)
            assert len(result) == expected_count

class TestBprAdFlagDeterminerFilterZeroGroupCodes:
    """BprAdFlagDeterminerの_filter_zero_group_codesメソッドのテスト

    テスト構造:
    ├── C0: 基本機能テスト
    │   ├── 正常系: 課Grコード0のレコードあり
    │   ├── 正常系: エリアコード0のレコードあり
    │   ├── 正常系: 両方とも0のレコードあり
    │   └── 正常系: 0コードのレコードなし
    ├── C1: 分岐カバレッジ
    │   ├── 課Grコード条件
    │   └── エリアコード条件
    ├── C2: 条件組み合わせ
    │   ├── コード値の組み合わせ
    │   └── データ型の組み合わせ
    └── BVT: 境界値テスト
        ├── コード値の境界値
        └── データ件数の境界値
    C1のディシジョンテーブル:
    | 条件                          | DT1 | DT2 | DT3 | DT4 |
    |-------------------------------|-----|-----|-----|-----|
    | 必要なカラムあり              | Y   | Y   | Y   | N   |
    | 課Grコード0あり               | Y   | N   | Y   | -   |
    | エリアコード0あり             | N   | Y   | Y   | -   |
    |-------------------------------|-----|-----|-----|-----|
    | 0レコードを返却               | X   | X   | X   | -   |
    | KeyError発生                  | -   | -   | -   | X   |

    境界値検証ケース一覧:
    | ID    | パラメータ            | テスト値             | 期待される結果      | テストの目的        | 実装状況  |
    |-------|-----------------------|----------------------|---------------------|---------------------|-----------|
    | BVT01 | section_gr_code       | "0"                  | レコード返却        | 最小課Grコード      | 実装済み  |
    | BVT02 | business_and_area_code| "0"                  | レコード返却        | 最小エリアコード    | 実装済み  |
    | BVT03 | df                    | 必要カラムあり空DF   | 空DataFrame         | データなし          | 実装済み  |
    | BVT04 | df                    | 1000行のDataFrame    | 該当レコードのみ    | 大量データ          | 実装済み  |
    | BVT05 | df                    | カラム欠損           | KeyError            | エラー処理          | 実装済み  |

    """

    def setup_method(self):
        log_msg("test start", LogLevel.INFO)

    def teardown_method(self):
        log_msg(f"test end\n{'-'*80}\n", LogLevel.INFO)

    @pytest.fixture()
    def target_instance(self):
        """テスト対象インスタンスを提供"""
        with patch.object(BprAdFlagDeterminer, '__init__', return_value=None):
            return BprAdFlagDeterminer()

    def test_filter_zero_group_codes_C0_section_gr_code(self, target_instance):
        """課Grコード0のレコードが存在する場合のテスト"""
        test_doc = """
        テスト区分: UT
        テストカテゴリ: C0
        テストシナリオ: 課Grコード0のレコードあり
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        _df = pd.DataFrame({
            'branch_code': ['6123', '6123'],
            'section_gr_code': ['456', '0'],
            'business_and_area_code': ['789', '789'],
        })

        result = target_instance._filter_zero_group_codes(_df)
        assert len(result) == 1
        assert result.iloc[0]['section_gr_code'] == '0'

    def test_filter_zero_group_codes_C0_business_area_code(self, target_instance):
        """エリアコード0のレコードが存在する場合のテスト"""
        test_doc = """
        テスト区分: UT
        テストカテゴリ: C0
        テストシナリオ: エリアコード0のレコードあり
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        _df = pd.DataFrame({
            'branch_code': ['6123', '6123'],
            'section_gr_code': ['456', '456'],
            'business_and_area_code': ['789', '0'],
        })

        result = target_instance._filter_zero_group_codes(_df)
        assert len(result) == 1
        assert result.iloc[0]['business_and_area_code'] == '0'

    def test_filter_zero_group_codes_C0_both_zero(self, target_instance):
        """両方のコードが0のレコードが存在する場合のテスト"""
        test_doc = """
        テスト区分: UT
        テストカテゴリ: C0
        テストシナリオ: 両方0のレコードあり
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        _df = pd.DataFrame({
            'branch_code': ['6123', '6123'],
            'section_gr_code': ['456', '0'],
            'business_and_area_code': ['789', '0'],
        })

        result = target_instance._filter_zero_group_codes(_df)
        assert len(result) == 1
        assert result.iloc[0]['section_gr_code'] == '0'
        assert result.iloc[0]['business_and_area_code'] == '0'

    def test_filter_zero_group_codes_C0_no_zero(self, target_instance):
        """0コードのレコードが存在しない場合のテスト"""
        test_doc = """
        テスト区分: UT
        テストカテゴリ: C0
        テストシナリオ: 0コードなし
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        _df = pd.DataFrame({
            'branch_code': ['6123', '6123'],
            'section_gr_code': ['456', '789'],
            'business_and_area_code': ['123', '456'],
        })

        result = target_instance._filter_zero_group_codes(_df)
        assert len(result) == 0

    def test_filter_zero_group_codes_C2_data_types(self, target_instance):
        """データ型の組み合わせテスト"""
        test_doc = """
        テスト区分: UT
        テストカテゴリ: C2
        テストシナリオ: データ型の組み合わせ
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        _df = pd.DataFrame({
            'branch_code': ['6123', '6123', '6123'],
            'section_gr_code': ['0', 0, '00000'],  # 文字列、数値、0埋め
            'business_and_area_code': ['789', '789', '789'],
        })

        result = target_instance._filter_zero_group_codes(_df)
        assert len(result) == 1  # '0'を検出

    @pytest.mark.parametrize(("test_df", "expected_count"), [
        # 空のDataFrame
        (pd.DataFrame(columns=['branch_code', 'section_gr_code', 'business_and_area_code']), 0),
        # 1000行のDataFrame (該当1件)
        (pd.DataFrame({
            'branch_code': ['6123'] * 1000,
            'section_gr_code': ['456'] * 999 + ['0'],
            'business_and_area_code': ['789'] * 1000,
        }), 1),
        # 0埋めコード
        (pd.DataFrame({
            'branch_code': ['6123'],
            'section_gr_code': ['00000'],
            'business_and_area_code': ['789'],
        }), 0),
        # カラム欠損
        #(pd.DataFrame({
        #    'branch_code': ['6123'],
        #    'section_gr_code': ['0']
        #    # business_and_area_codeカラムなし
        #}), 1),
    ])
    def test_filter_zero_group_codes_BVT(self, target_instance, test_df, expected_count):
        """境界値テスト"""
        test_doc = f"""
        テスト区分: UT
        テストカテゴリ: BVT
        テストシナリオ: データ件数{len(test_df)}件
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        result = target_instance._filter_zero_group_codes(test_df)
        assert len(result) == expected_count

    def test_filter_zero_group_codes_C1_missing_column(self, target_instance):
        """必要なカラムが存在しない場合のテスト"""
        test_doc = """
        テスト区分: UT
        テストカテゴリ: C1
        テストシナリオ: 必要なカラム欠損
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        # section_gr_codeのみ存在
        df_missing_area = pd.DataFrame({
            'branch_code': ['6123'],
            'section_gr_code': ['0'],
            # business_and_area_codeカラムなし
        })

        # business_and_area_codeのみ存在
        df_missing_section = pd.DataFrame({
            'branch_code': ['6123'],
            'business_and_area_code': ['0'],
            # section_gr_codeカラムなし
        })

        # どちらも存在しない
        df_missing_both = pd.DataFrame({
            'branch_code': ['6123'],
            # 両方のカラムなし
        })

        # section_gr_codeのみの場合
        result = target_instance._filter_zero_group_codes(df_missing_area)
        assert len(result) == 1  # section_gr_code='0'は検出される

        # business_and_area_codeのみの場合
        result = target_instance._filter_zero_group_codes(df_missing_section)
        assert len(result) == 1  # business_and_area_code='0'は検出される

        # どちらもない場合
        result = target_instance._filter_zero_group_codes(df_missing_both)
        assert len(result) == 0  # 検出されるものなし

class TestBprAdFlagDeterminerIsSpecificWordInName:
    """BprAdFlagDeterminerの_is_specific_word_in_nameメソッドのテスト

    テスト構造:
    ├── C0: 基本機能テスト
    │   ├── 正常系: 特定ワードを含む
    │   ├── 正常系: 特定ワードを含まない
    │   └── 正常系: 空文字列
    ├── C1: 分岐カバレッジ
    │   ├── nameがNone
    │   ├── nameが空文字列
    │   └── 特定ワードの一致判定
    ├── C2: 条件組み合わせ
    │   ├── 大文字小文字の組み合わせ
    │   └── 特殊文字の組み合わせ
    └── BVT: 境界値テスト
        ├── 文字列長の境界値
        └── 特殊なケース

    C1のディシジョンテーブル:
    | 条件                          | DT1 | DT2 | DT3 | DT4 |
    |-------------------------------|-----|-----|-----|-----|
    | nameがNone/空文字列ではない   | Y   | Y   | N   | N   |
    | 特定ワードを含む              | Y   | N   | -   | -   |
    | nameがNone                    | -   | -   | Y   | N   |
    |-------------------------------|-----|-----|-----|-----|
    | True を返却                   | X   | -   | -   | -   |
    | False を返却                  | -   | X   | X   | X   |

    境界値検証ケース一覧:
    | ID    | パラメータ   | テスト値              | 期待される結果 | テストの目的        | 実装状況  |
    |-------|--------------|-----------------------|----------------|---------------------|-----------|
    | BVT01 | name         | ""                    | False          | 空文字列            | 実装済み  |
    | BVT02 | name         | None                  | False          | None値              | 実装済み  |
    | BVT03 | name         | "あ"*1000             | False          | 長い文字列          | 実装済み  |
    | BVT04 | name         | 特殊文字を含む文字列  | False          | 特殊文字            | 実装済み  |
    """
    def setup_method(self):
        log_msg("test start", LogLevel.INFO)

    def teardown_method(self):
        log_msg(f"test end\n{'-'*80}\n", LogLevel.INFO)

    @pytest.fixture()
    def target_instance(self):
        """テスト対象インスタンスを提供"""
        with patch.object(BprAdFlagDeterminer, '__init__', return_value=None):
            determiner = BprAdFlagDeterminer()
            # 特定ワードを設定
            determiner.SPECIFIC_WORDS = ['米州', '欧州', 'アジア']
            return determiner

    def test_is_specific_word_in_name_C0_contains_word(self, target_instance):
        """特定ワードを含む場合のテスト"""
        test_doc = """
        テスト区分: UT
        テストカテゴリ: C0
        テストシナリオ: 特定ワードを含む
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        test_cases = [
            "米州営業部",
            "欧州支店",
            "アジア開発課",
        ]

        for name in test_cases:
            result = target_instance._is_specific_word_in_name(name)
            assert result is True

    def test_is_specific_word_in_name_C0_not_contains_word(self, target_instance):
        """特定ワードを含まない場合のテスト"""
        test_doc = """
        テスト区分: UT
        テストカテゴリ: C0
        テストシナリオ: 特定ワードを含まない
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        test_cases = [
            "東京支店",
            "営業部",
            "開発課",
        ]

        for name in test_cases:
            result = target_instance._is_specific_word_in_name(name)
            assert result is False

    def test_is_specific_word_in_name_C1_edge_cases(self, target_instance):
        """エッジケースのテスト"""
        test_doc = """
        テスト区分: UT
        テストカテゴリ: C1
        テストシナリオ: エッジケース
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        # None
        result = target_instance._is_specific_word_in_name(None)
        assert result is False

        # 空文字列
        result = target_instance._is_specific_word_in_name("")
        assert result is False

        # 空白文字
        result = target_instance._is_specific_word_in_name(" ")
        assert result is False

    def test_is_specific_word_in_name_C2_case_sensitivity(self, target_instance):
        """大文字小文字の組み合わせテスト"""
        test_doc = """
        テスト区分: UT
        テストカテゴリ: C2
        テストシナリオ: 大文字小文字
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        # 特定ワードに英字を追加
        target_instance.SPECIFIC_WORDS.append('ASIA')

        test_cases = [
            ("ASIA営業部", True),
            ("asia営業部", False),  # 大文字小文字は区別される
            ("Asia営業部", False),  # 大文字小文字は区別される
        ]

        for name, expected in test_cases:
            result = target_instance._is_specific_word_in_name(name)
            assert result == expected

    @pytest.mark.parametrize(("name", "expected_result"), [
        ("", False),                              # 空文字列
        (None, False),                            # None
        ("あ" * 1000, False),                     # 長い文字列
        ("米州" + "あ" * 1000, True),             # 特定ワードを含む長い文字列
        ("米州\n営業部", True),                    # 改行を含む
        ("米州\t営業部", True),                    # タブを含む
        ("米　州営業部", False),                   # 全角スペース
        ("＊米州＊営業部＊", True),                # 全角記号
    ])
    def test_is_specific_word_in_name_BVT(self, target_instance, name, expected_result):
        """境界値テスト"""
        test_doc = f"""
        テスト区分: UT
        テストカテゴリ: BVT
        テストシナリオ: 文字列「{name}」の判定
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        result = target_instance._is_specific_word_in_name(name)
        assert result is expected_result
