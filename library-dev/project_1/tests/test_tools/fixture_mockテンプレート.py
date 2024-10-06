"""testにおいてpatchを適用するが、実際に適用されたのか・その値も確認する方針とする"""

import sys
from unittest.mock import MagicMock, patch

import pandas as pd
import pytest

from src.lib.common_utils.ibr_decorator_config import initialize_config
from src.lib.common_utils.ibr_enums import LogLevel
from src.lib.common_utils.ibr_pickled_table_searcher import TableSearcher

config = initialize_config(sys.modules[__name__])
log_msg = config.log_message

class TestTableSearcherNormalizeConditions:
    @pytest.fixture()
    def mock_searcher(self):
        def mock_get_file_modified_time():
            timestamp = 12345.0
            log_msg(f"Mock _default_get_file_modified_time called, returning {timestamp}", LogLevel.DEBUG)
            return timestamp

        def mock_load_table():
            _df = pd.DataFrame({'test_column': [1, 2, 3]})
            log_msg(f"Mock _default_load_table called, returning DataFrame with shape {_df.shape}", LogLevel.DEBUG)
            return _df

        with patch('src.lib.common_utils.ibr_pickled_table_searcher.TableSearcher._default_get_file_modified_time',
                side_effect=mock_get_file_modified_time) as mock_get_time, \
            patch('src.lib.common_utils.ibr_pickled_table_searcher.TableSearcher._default_load_table',
                side_effect=mock_load_table) as mock_load:

            log_msg("Creating mock TableSearcher instance", LogLevel.DEBUG)
            searcher = TableSearcher("test_table.pkl")

            # パッチが適用されたことを確認
            log_msg(f"_default_get_file_modified_time called: {mock_get_time.called}", LogLevel.DEBUG)
            log_msg(f"_default_load_table called: {mock_load.called}", LogLevel.DEBUG)

            # 実際に返された値を確認
            if mock_get_time.called:
                log_msg(f"Actual value returned by _default_get_file_modified_time: {searcher.last_modified_time}", LogLevel.DEBUG)
            if mock_load.called:
                log_msg(f"Actual DataFrame returned by _default_load_table: shape {searcher.df.shape}, columns {searcher.df.columns}", LogLevel.DEBUG)

            yield searcher

#--------------------------------------------------
# 以下はfixture-patchを使ったテストコード例
#--------------------------------------------------
    def test_normalize_conditions_C0_dict(self, mock_searcher):
        test_doc = """
        テスト区分: UT
        テストカテゴリ: C0
        テスト内容: 辞書型の条件を正規化
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        conditions = {"column1": "value1"}
        log_msg("Calling _normalize_conditions", LogLevel.DEBUG)
        result = mock_searcher._normalize_conditions(conditions)
        log_msg(f"_normalize_conditions result: {result}", LogLevel.DEBUG)

        assert isinstance(result, list)
        assert len(result) == 1
        assert result[0] == conditions

"""
2024-10-06 23:40:50 [INFO] common_utils.test_ibr_pickled_table_searcher::mock_get_file_modified_time line 990: Mock _default_get_file_modified_time called, returning 12345.0:
2024-10-06 23:40:50 [INFO] common_utils.test_ibr_pickled_table_searcher::mock_load_table line 995: Mock _default_load_table called, returning DataFrame with shape (3, 1):
2024-10-06 23:40:50 [INFO] common_utils.test_ibr_pickled_table_searcher::mock_searcher line 1007: _default_get_file_modified_time called: True:
2024-10-06 23:40:50 [INFO] common_utils.test_ibr_pickled_table_searcher::mock_searcher line 1008: _default_load_table called: True:
2024-10-06 23:40:50 [INFO] common_utils.test_ibr_pickled_table_searcher::mock_searcher line 1012: Actual value returned by _default_get_file_modified_time: 12345.0:
2024-10-06 23:40:50 [INFO] common_utils.test_ibr_pickled_table_searcher::mock_searcher line 1014: Actual DataFrame returned by _default_load_table: shape (3, 1), columns Index(['test_column'], dtype='object'):
2024-10-06 23:40:50 [INFO] common_utils.test_ibr_pickled_table_searcher::test_normalize_conditions_C0_dict line 1024:

"""
