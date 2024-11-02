import pickle
import sys
from datetime import datetime, timedelta
from io import StringIO
from pathlib import Path
from unittest.mock import MagicMock, patch

import numpy as np
import pandas as pd
import pytest
import ulid
from tabulate import tabulate
from ulid import ULID

from src.lib.common_utils.ibr_dataframe_helper import tabulate_dataframe
from src.lib.common_utils.ibr_decorator_config import initialize_config
from src.lib.common_utils.ibr_enums import LogLevel
from src.lib.common_utils.ibr_pickled_table_searcher import ErrorMessages, TableSearcher

# config共有
config = initialize_config(sys.modules[__name__])
log_msg = config.log_message

"""
| No | Column名称(日本語)   | column_name(python)  | 属性 | 桁数/文字数 | Column説明(略) |
|---:|:---------------------|:---------------------|:-----|:------------|:---------------|
| 1  | 種類                 | application_type     | str  | 1           | 新設/変更/廃止 |
| 2  | 対象                 | target_org           | str  | -           |
| 3  | 部門コード           | business_unit_code   | str  | 3           | - |
| 4  | 親部店コード         | parent_branch_code   | str  | 5           | - |
| 5  | 部店コード           | branch_code          | str  | 5           | - |
| 6  | 部店名称             | branch_name          | str  | 78          | - |
| 7  | 課Grコード           | section_gr_code      | str  | 5           | - |
| 8  | 課Gr名称             | section_gr_name      | str  | 48          | - |
| 9  | 課名称(英語)         | section_name_en      | str  | 75          | - |
| 10 | 共通認証受渡し予定日 | aaa_transfer_date    | str  | 8           | - |
| 11 | 部店カナ             | branch_name_kana     | str  | 48          | ブランク |
| 12 | 課Gr名称(カナ)       | section_gr_name_kana | str  | 48          | - |
| 13 | 課Gr名称(略称)       | section_gr_name_abbr | str  | 10          | - |
| 14 | BPR対象/対象外フラグ | bpr_target_flag      | str  | 1           | - |

"""

def generate_sample_data(num_records=10):
    data = []
    
    for _ in range(num_records):
        record = {
            "application_type": np.random.choice(["1", "2", "3"]),  # 1: 新設, 2: 変更, 3: 廃止
            "target_org": np.random.choice(["部店", "課", "エリア", "拠点内営業部", "課/エリア", "課/エリア(拠点内営業部)"]),
            "business_unit_code": f"{np.random.randint(100, 999):03d}",
            "parent_branch_code": f"{np.random.randint(10000, 99999):05d}",
            "branch_code": f"{np.random.randint(10000, 99999):05d}",
            "branch_name": f"支店{np.random.randint(1, 100)}".ljust(78),
            "section_gr_code": f"{np.random.randint(10000, 99999):05d}",
            "section_gr_name": f"部署{np.random.randint(1, 100)}".ljust(48),
            "section_name_en": f"Section {np.random.randint(1, 100)}".ljust(75),
            "aaa_transfer_date": datetime.now().strftime("%Y%m%d"),
            "branch_name_kana": "".ljust(48),  # ブランク
            "section_gr_name_kana": f"ブモン{np.random.randint(1, 100)}".ljust(48),
            "section_gr_name_abbr": f"部{np.random.randint(1, 100)}".ljust(10),
            "bpr_target_flag": np.random.choice(["0", "1"])
        }
        data.append(record)
    
    return pd.DataFrame(data)

def generate_sample_data_from_docstrig(df: pd.DataFrame) -> pd.DataFrame:
    # Excel -> データコピー -> エディターでペースト/tab区切り確認 -> エディターからdocstringとしてコピペ
    docstring = """
    """
    # docstringが空の場合は空のDataFrameを返す
    if docstring.isspace():
        return df 

    return pd.read_csv(
        StringIO(docstring),
        header=0,
        sep=r'\s+',
        dtype='object',
    )

# サンプルDataFrameの生成
# ランダム生成 or docstringからの生成、どちらかを選ぶ
df = generate_sample_data()
df = generate_sample_data_from_docstrig(df)

# オプション:DataFrameをExcel/pickleファイルに保存
df.to_excel("tests/table/sample_関連申請.xlsx", index=False)
df.to_pickle('tests/table/kanren.pkl')

# pickle file 読み込み確認
kanren = TableSearcher('kanren.pkl', 'tests/table/')
log_msg(f'\n\n{tabulate_dataframe(kanren.df)}')
