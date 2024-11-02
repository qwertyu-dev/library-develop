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
| No  | Column名称(日本語)                                | column_name(python)         | 属性 | 桁数/文字数 |
|----:|:--------------------------------------------------|:----------------------------|:-----|:------------|
|   1 | 報告日                                            | report_date                 | str  | -           |
|   2 | no                                                | application_number          | int  | -           |
|   3 | 有効日付                                          | effective_date              | str  | -           |
|   4 | 種類                                              | application_type            | str  | -           |
|   5 | 対象                                              | target_org                  | str  | -           |
|   6 | 部門コード                                        | business_unit_code          | str  | -           |
|   7 | 親部店コード                                      | parent_branch_code          | str  | -           |
|   8 | 部店コード                                        | branch_code                 | str  | -           |
|   9 | 部店名称                                          | branch_name                 | str  | -           |
|  10 | 部店名称(英語)                                    | branch_name_en              | str  | -           |
|  11 | 課/エリアコード                                   | section_area_code           | str  | -           |
|  12 | 課/エリア名称                                     | section_area_name           | str  | -           |
|  13 | 課/エリア名称(英語)                               | section_area_name_en        | str  | -           |
|  14 | 常駐部店コード                                    | resident_branch_code        | str  | -           |
|  15 | 常駐部店名称                                      | resident_branch_name        | str  | -           |
|  16 | 純新規店の組織情報受渡し予定日(開店日基準)        | new_org_info_transfer_date  | str  | -           |
|  17 | 共通認証受渡し予定日(人事データ反映基準)          | aaa_transfer_date           | str  | -           |
|  18 | 備考                                              | remarks                     | str  | -           |
"""

def generate_sample_data(num_records=10):
    data = []
    
    for i in range(num_records):
        report_date = datetime.now() - timedelta(days=np.random.randint(0, 365))
        effective_date = report_date + timedelta(days=np.random.randint(1, 180))
        
        record = {
            "report_date": report_date.strftime("%Y-%m-%d"),
            "application_number": i + 1,
            "effective_date": effective_date.strftime("%Y-%m-%d"),
            "application_type": np.random.choice(["新設", "変更", "廃止"]),
            "target_org": np.random.choice(["部店", "課", "エリア", "拠点内営業部", "課/エリア", "課/エリア(拠点内営業部)"]),
            "business_unit_code": f"{np.random.randint(100, 999):03d}",
            "parent_branch_code": f"{np.random.randint(10000, 99999):05d}",
            "branch_code": f"{np.random.randint(10000, 99999):05d}",
            "branch_name": f"支店{np.random.randint(1, 100)}",
            "branch_name_en": f"Branch {np.random.randint(1, 100)}",
            "section_area_code": f"{np.random.randint(1000, 9999):04d}",
            "section_area_name": f"部署{np.random.randint(1, 100)}",
            "section_area_name_en": f"Section {np.random.randint(1, 100)}",
            "resident_branch_code": f"{np.random.randint(10000, 99999):05d}",
            "resident_branch_name": f"常駐支店{np.random.randint(1, 100)}",
            "new_org_info_transfer_date": (effective_date - timedelta(days=np.random.randint(1, 30))).strftime("%Y-%m-%d"),
            "aaa_transfer_date": (effective_date - timedelta(days=np.random.randint(1, 15))).strftime("%Y-%m-%d"),
            "remarks": f"備考{np.random.randint(1, 100)}"
        }
        data.append(record)
    
    return pd.DataFrame(data)

def generate_sample_data_from_docstrig(df) -> pd.DataFrame:
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

# オプション: DataFrameをExcel/pickleファイルに保存
df.to_excel("tests/table/sample_人事.xlsx", index=False)
df.to_pickle('tests/table/jinji.pkl')

# pickle file 読み込み確認
jinji = TableSearcher('jinji.pkl', 'tests/table/')
log_msg(f'\n\n{tabulate_dataframe(jinji.df)}')
