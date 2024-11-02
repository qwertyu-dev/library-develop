import pickle
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pandas as pd
import pytest

from src.lib.common_utils.ibr_dataframe_helper import tabulate_dataframe
from src.lib.common_utils.ibr_decorator_config import initialize_config
from src.lib.common_utils.ibr_enums import LogLevel
from src.lib.common_utils.ibr_pickled_table_searcher import ErrorMessages, TableSearcher

# config共有
config = initialize_config(sys.modules[__name__])
log_msg = config.log_message

def main():
    log_msg(f'start: import')
    # デフォルト位置のpickle読み込みケース
    jinji = TableSearcher('jinji_requests.pkl')
    log_msg(f'\n\n{tabulate_dataframe(jinji.df)}')

    # path指定してのpickle読み込みケース
    integrated = TableSearcher('integrated_layout.pkl', file_path='tests/table')
    log_msg(f'\n\n{tabulate_dataframe(integrated.df)}')

if __name__ == "__main__":
    main()
