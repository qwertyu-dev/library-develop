import pytest
from pathlib import Path
import pandas as pd
from unittest.mock import Mock, patch
import ulid

####################################
# テスト対象モジュールimport
####################################
from src.lib.converter_utils.ibr_mapping_layout_excel_to_integrated import ExcelProcessor, ExcelProcessorError, InvalidFileError, InvalidDataError

from src.lib.converter_utils.ibr_mapping_layout_excel_to_integrated import JinjiExcelProcessor

####################################
# テストサポートモジュールimport
####################################
from src.lib.common_utils.ibr_enums import LogLevel
from src.lib.common_utils.ibr_get_config import Config

package_path = Path(__file__)
config = Config.load(package_path)

log_msg = config.log_message
log_msg(str(config), LogLevel.DEBUG)

class TestExcelProcessorProcess:
    """ExcelProcessorのprocessメソッドのテスト

    テスト構造:
    ├── C0: 基本機能テスト
    │   ├── 正常系: 有効なファイルパスでの処理
    │   ├── 異常系: 無効なファイルパスでの処理
    │   └── 異常系: データ検証エラー
    ├── C1: 分岐カバレッジ
    │   ├── 正常系: 全ての処理が正常に完了
    │   ├── 異常系: read_and_mapでの例外発生
    │   ├── 異常系: validate_dataでの例外発生
    │   └── 異常系: map_to_unified_layoutでの例外発生
    └── C2: 条件組み合わせ
        ├── 正常系: 全てのメソッドが正常に動作
        ├── 異常系: read_and_mapがInvalidFileErrorを発生
        ├── 異常系: validate_dataがInvalidDataErrorを発生
        └── 異常系: map_to_unified_layoutが予期せぬ例外を発生

    # C1のディシジョンテーブル
    | 条件                          | ケース1 | ケース2 | ケース3 | ケース4 |
    |-------------------------------|---------|---------|---------|---------|
    | read_and_mapが成功            | Y       | N       | Y       | Y       |
    | validate_dataが成功           | Y       | -       | N       | Y       |
    | map_to_unified_layoutが成功   | Y       | -       | -       | N       |
    | 出力                          | 成功    | 例外    | 例外    | 例外    |
    """

    def setup_method(self):
        log_msg("test start", LogLevel.INFO)

    def teardown_method(self):
        log_msg(f"test end\n{'-'*80}\n", LogLevel.INFO)

    @pytest.fixture()
    def mock_excel_processor(self):
        class MockExcelProcessor(ExcelProcessor):
            def read_and_map(self, file_path: str) -> pd.DataFrame:
                return pd.DataFrame({'test': [1, 2, 3]})

            def validate_data(self, df: pd.DataFrame) -> None:
                pass

            def map_to_unified_layout(self, df: pd.DataFrame) -> pd.DataFrame:
                return df

        return MockExcelProcessor()

    def test_process_C0_valid_file(self, mock_excel_processor):
        test_doc = """テスト内容:
        C0テスト: 正常系 - 有効なファイルパスでの処理
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        result = mock_excel_processor.process('valid_file.xlsx')
        assert isinstance(result, pd.DataFrame)
        assert not result.empty

    def test_process_C0_invalid_file(self, mock_excel_processor):
        test_doc = """テスト内容:
        C0テスト: 異常系 - 無効なファイルパスでの処理
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        with patch.object(mock_excel_processor, 'read_and_map', side_effect=InvalidFileError), pytest.raises(InvalidFileError):
                mock_excel_processor.process('invalid_file.xlsx')

    def test_process_C0_data_validation_error(self, mock_excel_processor):
        test_doc = """テスト内容:
        C0テスト: 異常系 - データ検証エラー
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        with patch.object(mock_excel_processor, 'validate_data', side_effect=InvalidDataError), pytest.raises(InvalidDataError):
                mock_excel_processor.process('valid_file.xlsx')

    def test_process_C1_all_success(self, mock_excel_processor):
        test_doc = """テスト内容:
        C1テスト: 正常系 - 全ての処理が正常に完了
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        result = mock_excel_processor.process('valid_file.xlsx')
        assert isinstance(result, pd.DataFrame)
        assert not result.empty

    def test_process_C1_read_and_map_exception(self, mock_excel_processor):
        test_doc = """テスト内容:
        C1テスト: 異常系 - read_and_mapでの例外発生
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        with patch.object(mock_excel_processor, 'read_and_map', side_effect=Exception('Test exception')), pytest.raises(ExcelProcessorError):
                mock_excel_processor.process('valid_file.xlsx')

    def test_process_C1_validate_data_exception(self, mock_excel_processor):
        test_doc = """テスト内容:
        C1テスト: 異常系 - validate_dataでの例外発生
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        with patch.object(mock_excel_processor, 'validate_data', side_effect=Exception('Test exception')), pytest.raises(ExcelProcessorError):
                mock_excel_processor.process('valid_file.xlsx')

    def test_process_C1_map_to_unified_layout_exception(self, mock_excel_processor):
        test_doc = """テスト内容:
        C1テスト: 異常系 - map_to_unified_layoutでの例外発生
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        with patch.object(mock_excel_processor, 'map_to_unified_layout', side_effect=Exception('Test exception')), pytest.raises(ExcelProcessorError):
                mock_excel_processor.process('valid_file.xlsx')

    def test_process_C2_all_methods_success(self, mock_excel_processor):
        test_doc = """テスト内容:
        C2テスト: 正常系 - 全てのメソッドが正常に動作
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        result = mock_excel_processor.process('valid_file.xlsx')
        assert isinstance(result, pd.DataFrame)
        assert not result.empty

    def test_process_C2_read_and_map_invalid_file_error(self, mock_excel_processor):
        test_doc = """テスト内容:
        C2テスト: 異常系 - read_and_mapがInvalidFileErrorを発生
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        with patch.object(mock_excel_processor, 'read_and_map', side_effect=InvalidFileError('Test error')), pytest.raises(InvalidFileError):
                mock_excel_processor.process('invalid_file.xlsx')

    def test_process_C2_validate_data_invalid_data_error(self, mock_excel_processor):
        test_doc = """テスト内容:
        C2テスト: 異常系 - validate_dataがInvalidDataErrorを発生
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        with patch.object(mock_excel_processor, 'validate_data', side_effect=InvalidDataError('Test error')), pytest.raises(InvalidDataError):
                mock_excel_processor.process('valid_file.xlsx')

    def test_process_C2_map_to_unified_layout_unexpected_error(self, mock_excel_processor):
        test_doc = """テスト内容:
        C2テスト: 異常系 - map_to_unified_layoutが予期せぬ例外を発生
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        with patch.object(mock_excel_processor, 'map_to_unified_layout', side_effect=ValueError('Unexpected error')), pytest.raises(ExcelProcessorError):
                mock_excel_processor.process('valid_file.xlsx')

# TODO(suzuki): - Kokukiのテストコード作成
# TODO(suzuki): - KanrenWithのテストコード作成
# TODO(suzuki): - KanrenWithoutのテストコード作成

class TestJinjiExcelProcessorReadAndMap:
    """JinjiExcelProcessorのread_and_mapメソッドのテスト

    テスト構造:
    ├── C0: 基本機能テスト
    │   ├── 正常系: 有効なExcelファイルの読み込み
    │   ├── 異常系: 無効なファイルパス
    │   └── 異常系: 必須列が欠けているExcelファイル
    ├── C1: 分岐カバレッジ
    │   ├── 正常系: 全ての列が存在する場合
    │   └── 異常系: 一部の列が欠けている場合
    └── C2: 条件組み合わせ
        ├── 正常系: 全ての列が正しい型で存在
        └── 異常系: 空のExcelファイル

    # C1のディシジョンテーブル
    | 条件                      | ケース1 | ケース2 |
    |---------------------------|---------|---------|
    | Excelファイルが読み込める | Y       | Y       |
    | 全ての必須列が存在する    | Y       | N       |
    | 出力                      | 成功    | 例外    |
    """

    def setup_method(self):
        self.processor = JinjiExcelProcessor()
        log_msg("test start", LogLevel.INFO)

    def teardown_method(self):
        log_msg(f"test end\n{'-'*80}\n", LogLevel.INFO)

    @pytest.fixture()
    def valid_excel_data(self):
        data = {
            '報告日': ['2024/07/20'],
            'no': [1],
            '有効日付': ['2024/08/01'],
            '種類': ['新設'],
            '対象': ['部'],
            '部門コード': ['001'],
            '親部店コード': ['00000'],
            '部店コード': ['10000'],
            '部店名称': ['テスト部店'],
            '部店名称(英語)': ['Test Branch'],
            '課/エリアコード': ['20000'],
            '課/エリア名称': ['テスト課'],
            '課/エリア名称(英語)': ['Test Section'],
            '常駐部店コード': ['30000'],
            '常駐部店名称': ['常駐テスト部店'],
            '純新規店の組織情報受渡し予定日(開店日基準)': ['2024/08/15'],
            '共通認証受渡し予定日(人事データ反映基準)': ['2024/08/10'],
            '備考': ['テスト用データ'],
        }
        return pd.DataFrame(data)

    def test_read_and_map_C0_valid_file(self, valid_excel_data):
        test_doc = """テスト内容:
        C0テスト: 正常系 - 有効なExcelファイルの読み込み
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        with patch('pandas.read_excel', return_value=valid_excel_data):
            result = self.processor.read_and_map('valid_file.xlsx')

        assert isinstance(result, pd.DataFrame)
        assert not result.empty
        assert 'application_number' in result.columns
        assert 'branch_name' in result.columns

    def test_read_and_map_C0_invalid_file_path(self):
        test_doc = """テスト内容:
        C0テスト: 異常系 - 無効なファイルパス
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        with patch('pandas.read_excel', side_effect=FileNotFoundError), pytest.raises(InvalidFileError):
                self.processor.read_and_map('invalid_file.xlsx')

    def test_read_and_map_C0_missing_required_columns(self):
        test_doc = """テスト内容:
        C0テスト: 異常系 - 必須列が欠けているExcelファイル
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        invalid_data = pd.DataFrame({'報告日': ['2024/07/20']})  # 必須列が欠けている
        with patch('pandas.read_excel', return_value=invalid_data), pytest.raises(InvalidDataError):
                self.processor.read_and_map('invalid_file.xlsx')

    def test_read_and_map_C1_all_columns_present(self, valid_excel_data):
        test_doc = """テスト内容:
        C1テスト: 正常系 - 全ての列が存在する場合
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        expected_columns = [
            'report_date', 'application_number', 'effective_date', 'application_type',
            'target_org', 'business_unit_code', 'parent_branch_code', 'branch_code',
            'branch_name', 'branch_name_en', 'section_area_code', 'section_area_name',
            'section_area_name_en', 'resident_branch_code', 'resident_branch_name',
            'new_org_info_transfer_date', 'aaa_transfer_date', 'remarks',
        ]

        with patch('pandas.read_excel', return_value=valid_excel_data):
            result = self.processor.read_and_map('valid_file.xlsx')

        assert isinstance(result, pd.DataFrame)
        assert not result.empty
        assert all(col in result.columns for col in expected_columns)

    def test_read_and_map_C1_missing_some_columns(self):
        test_doc = """テスト内容:
        C1テスト: 異常系 - 一部の列が欠けている場合
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        # JinjiExcelProcessorで期待される全ての列を含むが、'種類'列を欠いたデータフレームを作成
        invalid_data = pd.DataFrame({
            '報告日': ['2024/07/20'],
            'no': [1],
            '有効日付': ['2024/08/01'],
            '対象': ['部'],
            '部門コード': ['001'],
            '親部店コード': ['00000'],
            '部店コード': ['10000'],
            '部店名称': ['テスト部店'],
            '部店名称(英語)': ['Test Branch'],
            '課/エリアコード': ['20000'],
            '課/エリア名称': ['テスト課'],
            '課/エリア名称(英語)': ['Test Section'],
            '常駐部店コード': ['30000'],
            '常駐部店名称': ['常駐テスト部店'],
            '純新規店の組織情報受渡し予定日(開店日基準)': ['2024/08/15'],
            '共通認証受渡し予定日(人事データ反映基準)': ['2024/08/10'],
            '備考': ['テスト用データ'],
        })

        mock_file_path = 'mock_invalid_file.xlsx'
        with patch('pandas.read_excel', return_value=invalid_data), pytest.raises(InvalidDataError) as exc_info:
                self.processor.read_and_map(mock_file_path)

        assert "Excel file does not contain all required columns" in str(exc_info.value)

    def test_read_and_map_C2_empty_excel_file(self):
        test_doc = """テスト内容:
        C2テスト: 異常系 - 空のExcelファイル
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        empty_data = pd.DataFrame()
        with patch('pandas.read_excel', return_value=empty_data), pytest.raises(InvalidDataError):
                self.processor.read_and_map('empty_file.xlsx')

class TestJinjiExcelProcessorValidateData:
    """JinjiExcelProcessorのvalidate_dataメソッドのテスト

    テスト構造:
    ├── C0: 基本機能テスト
    │   ├── 正常系: 有効なデータフレーム
    │   └── 異常系: 必須項目が空のデータフレーム
    ├── C1: 分岐カバレッジ
    │   ├── 正常系: 全ての必須項目が存在し、null値がない
    │   └── 異常系: 一部の必須項目にnull値が含まれる
    └── C2: 条件組み合わせ
        ├── 正常系: 全ての列が正しいデータ型で存在
        └── 異常系: 必須項目以外の列にnull値が含まれる

    # C1のディシジョンテーブル
    | 条件                          | ケース1 | ケース2 | ケース3 | ケース4 |
    |-------------------------------|---------|---------|---------|---------|
    | application_typeが有効        | Y       | N       | Y       | Y       |
    | target_orgが有効              | Y       | Y       | N       | Y       |
    | branch_codeが有効             | Y       | Y       | Y       | N       |
    | branch_nameが有効             | Y       | Y       | Y       | Y       |
    | 出力                          | 成功    | 例外    | 例外    | 例外    |
    """

    def setup_method(self):
        self.processor = JinjiExcelProcessor()
        log_msg("test start", LogLevel.INFO)

    def teardown_method(self):
        log_msg(f"test end\n{'-'*80}\n", LogLevel.INFO)

    @pytest.fixture()
    def valid_data(self):
        return pd.DataFrame({
            'application_type': ['新設'],
            'target_org': ['部'],
            'branch_code': ['10000'],
            'branch_name': ['テスト部店'],
            'application_number': [1],
            'effective_date': ['2024/08/01'],
            'business_unit_code': ['001'],
            'parent_branch_code': ['00000'],
            'branch_name_en': ['Test Branch'],
            'section_area_code': ['20000'],
            'section_area_name': ['テスト課'],
            'section_area_name_en': ['Test Section'],
            'resident_branch_code': ['30000'],
            'resident_branch_name': ['常駐テスト部店'],
            'new_org_info_transfer_date': ['2024/08/15'],
            'aaa_transfer_date': ['2024/08/10'],
            'remarks': ['テスト用データ'],
        })

    def test_validate_data_C0_valid_data(self, valid_data):
        test_doc = """テスト内容:
        C0テスト: 正常系 - 有効なデータフレーム
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        self.processor.validate_data(valid_data)  # 例外が発生しないことを確認

    def test_validate_data_C0_missing_required_fields(self, valid_data):
        test_doc = """テスト内容:
        C0テスト: 異常系 - 必須項目が欠けているデータフレーム
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        # 'application_type'列を削除
        invalid_data = valid_data.drop(columns=['application_type'])

        # InvalidDataErrorが発生することを確認
        with pytest.raises(InvalidDataError) as exc_info:
            self.processor.validate_data(invalid_data)

        # 例外メッセージに欠けている列名が含まれていることを確認
        assert "Missing required columns: application_type" in str(exc_info.value)

    def test_validate_data_C1_all_valid(self, valid_data):
        test_doc = """テスト内容:
        C1テスト: 正常系 - 全ての必須項目が存在し、null値がない
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        self.processor.validate_data(valid_data)  # 例外が発生しないことを確認

    def test_validate_data_C1_null_values(self, valid_data):
        test_doc = """テスト内容:
        C1テスト: 異常系 - 一部の必須項目にnull値が含まれる
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        invalid_data = valid_data.copy()
        invalid_data.loc[0, 'branch_code'] = None
        with pytest.raises(InvalidDataError):
            self.processor.validate_data(invalid_data)

    def test_validate_data_C2_correct_data_types(self, valid_data):
        test_doc = """テスト内容:
        C2テスト: 正常系 - 全ての列が正しいデータ型で存在
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        self.processor.validate_data(valid_data)  # 例外が発生しないことを確認

    def test_validate_data_C2_null_in_non_required_field(self, valid_data):
        test_doc = """テスト内容:
        C2テスト: 異常系 - 必須項目以外の列にnull値が含まれる
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        invalid_data = valid_data.copy()
        invalid_data.loc[0, 'remarks'] = None
        self.processor.validate_data(invalid_data)  # 例外が発生しないことを確認


class TestJinjiExcelProcessorMapToUnifiedLayout:
    """JinjiExcelProcessorのmap_to_unified_layoutメソッドのテスト

    テスト構造:
    ├── C0: 基本機能テスト
    │   ├── 正常系: 有効なデータフレームの変換
    │   └── 異常系: 無効なデータフレーム
    ├── C1: 分岐カバレッジ
    │   ├── 正常系: target_orgが'課'の場合
    │   ├── 正常系: target_orgが'エリア'の場合
    │   └── 正常系: target_orgがその他の場合
    └── C2: 条件組み合わせ
        ├── 正常系: 全ての必須フィールドが存在
        ├── 異常系: 一部の必須フィールドが欠落
        ├── 正常系: ULID column生成の妥当性

    # C1のディシジョンテーブル
    | 条件                     | ケース1 | ケース2 | ケース3 |
    |--------------------------|---------|---------|---------|
    | target_orgが'課'         | Y       | N       | N       |
    | target_orgが'エリア'     | N       | Y       | N       |
    | target_orgがその他       | N       | N       | Y       |
    | 出力                     | 成功    | 成功    | 成功    |
    """

    def setup_method(self):
        self.processor = JinjiExcelProcessor()
        log_msg("test start", LogLevel.INFO)

    def teardown_method(self):
        log_msg(f"test end\n{'-'*80}\n", LogLevel.INFO)

    @pytest.fixture()
    def valid_input_data(self):
        return pd.DataFrame({
            'application_type': ['新設'],
            'target_org': ['課'],
            'business_unit_code': ['001'],
            'parent_branch_code': ['00000'],
            'branch_code': ['10000'],
            'branch_name': ['テスト部店'],
            'section_area_code': ['20000'],
            'section_area_name': ['テスト課'],
            'section_area_name_en': ['Test Section'],
            'resident_branch_code': ['30000'],
            'resident_branch_name': ['常駐テスト部店'],
            'aaa_transfer_date': ['2024/08/10'],
            'remarks': ['テスト用データ'],
        })

    def test_map_to_unified_layout_C0_valid_data(self, valid_input_data):
        test_doc = """テスト内容:
        C0テスト: 正常系 - 有効なデータフレームの変換
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        result = self.processor.map_to_unified_layout(valid_input_data)

        assert isinstance(result, pd.DataFrame)
        assert not result.empty
        assert all(col in result.columns for col in self.processor.unified_layout)
        assert len(result) == len(valid_input_data)

    def test_map_to_unified_layout_C0_invalid_data(self):
        test_doc = """テスト内容:
        C0テスト: 異常系 - 無効なデータフレーム
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        invalid_data = pd.DataFrame({'invalid_column': [1, 2, 3]})
        with pytest.raises(ExcelProcessorError):
            self.processor.map_to_unified_layout(invalid_data)

    def test_map_to_unified_layout_C1_target_org_section(self, valid_input_data):
        test_doc = """テスト内容:
        C1テスト: 正常系 - target_orgが'課'の場合
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        valid_input_data['target_org'] = '課'
        result = self.processor.map_to_unified_layout(valid_input_data)

        assert result['section_gr_code'].iloc[0] == valid_input_data['section_area_code'].iloc[0]
        assert result['section_gr_name'].iloc[0] == valid_input_data['section_area_name'].iloc[0]
        assert result['area_code'].iloc[0] == ''
        assert result['area_name'].iloc[0] == ''

    def test_map_to_unified_layout_C1_target_org_area(self, valid_input_data):
        test_doc = """テスト内容:
        C1テスト: 正常系 - target_orgが'エリア'の場合
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        valid_input_data['target_org'] = 'エリア'
        result = self.processor.map_to_unified_layout(valid_input_data)

        assert result['section_gr_code'].iloc[0] == ''
        assert result['section_gr_name'].iloc[0] == ''
        assert result['area_code'].iloc[0] == valid_input_data['section_area_code'].iloc[0]
        assert result['area_name'].iloc[0] == valid_input_data['section_area_name'].iloc[0]

    def test_map_to_unified_layout_C1_target_org_other(self, valid_input_data):
        test_doc = """テスト内容:
        C1テスト: 正常系 - target_orgがその他の場合
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        valid_input_data['target_org'] = '部'
        result = self.processor.map_to_unified_layout(valid_input_data)

        assert result['section_gr_code'].iloc[0] == ''
        assert result['section_gr_name'].iloc[0] == ''
        assert result['area_code'].iloc[0] == ''
        assert result['area_name'].iloc[0] == ''

    def test_map_to_unified_layout_C2_all_required_fields(self, valid_input_data):
        test_doc = """テスト内容:
        C2テスト: 正常系 - 全ての必須フィールドが存在
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        result = self.processor.map_to_unified_layout(valid_input_data)

        assert all(col in result.columns for col in self.processor.unified_layout)
        assert not result[self.processor.unified_layout].isna().any().any()

    def test_map_to_unified_layout_C2_missing_fields(self, valid_input_data):
        test_doc = """テスト内容:
        C2テスト: 異常系 - 一部の必須フィールドが欠落
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        invalid_data = valid_input_data.drop(columns=['branch_code'])
        with pytest.raises(ExcelProcessorError):
            self.processor.map_to_unified_layout(invalid_data)

    @patch('ulid.new')
    def test_map_to_unified_layout_ulid_generation(self, mock_ulid, valid_input_data):
        test_doc = """テスト内容:
        追加テスト: ULIDの生成確認
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        expected_ulid = '01ARZ3NDEKTSV4RRFFQ69G5FAV'
        mock_ulid.return_value = expected_ulid

        result = self.processor.map_to_unified_layout(valid_input_data)

        assert 'ulid' in result.columns
        assert result['ulid'].iloc[0] == expected_ulid
        assert mock_ulid.call_count == len(valid_input_data)
