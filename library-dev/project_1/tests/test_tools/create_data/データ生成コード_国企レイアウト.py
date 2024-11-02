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
| No  | Column名称(日本語)           | column_name(python)           | 属性 | 桁数/文字数 | Column説明(略)                           |
|----:|:-----------------------------|:----------------------------|:-----|:------------|:----------------------------------------|
|   1 | 報告日                       | report_date                 | str  | -           | 申請フォームのB4セルに報告日: MM/DD/     |
|   2 | no                           | application_number          | int  | -           | 半角数字                                |
|   3 | 登録予定日(yyyy/mm/dd)       | effective_date              | str  | -           | 半角数字                                |
|   4 | 種類(新規変更廃止)           | application_type            | str  | -           | 申請の種類(新設/変更/廃止のいずれか)    |
|   5 | 対象(課・エリア/中間階層)    | target_org                  | str  | -           | 申請対象の組織の階層(課・エリア/中間階層)|
|   6 | 部店店番                     | branch_code                 | str  | -           | 半角数字                                |
|   7 | 部店名称 日本語              | branch_name_ja              | str  | -           | -                                       |
|   8 | 部店名称 英語                | branch_name_en              | str  | -           | -                                       |
|   9 | 中間階層コード               | intermediate_level_code     | str  | -           | 統合レイアウトへの転記対象外            |
|  10 | 中間階層名称:日本語          | intermediate_level_name_ja  | str  | -           | 統合レイアウトへの転記対象外            |
|  11 | 中間階層名称:英語            | intermediate_level_name_en  | str  | -           | 統合レイアウトへの転記対象外            |
|  12 | 中間階層略称:日本語          | intermediate_level_abbr_ja  | str  | -           | 統合レイアウトへの転記対象外            |
|  13 | 中間階層略称:英語            | intermediate_level_abbr_en  | str  | -           | 統合レイアウトへの転記対象外            |
|  14 | 課・エリアコード             | section_area_code           | str  | -           | 課Grコード                              |
|  15 | 課・エリア名称:日本語        | section_area_name_ja        | str  | -           | 課Gr名称                                |
|  16 | 課・エリア名称:英語          | section_area_name_en        | str  | -           | 統合レイアウトへの転記対象外            |
|  17 | 課・エリア略称:日本語        | section_area_abbr_ja        | str  | -           | 統合レイアウトへの転記対象外            |
|  18 | 課・エリア略称:英語          | section_area_abbr_en        | str  | -           | 統合レイアウトへの転記対象外            |
|  19 | 共通認証受渡予定日           | aaa_transfer_date           | str  | -           | 共通認証への送信日                      |
|  20 | 変更種別・詳細旧名称・略語   | change_details              | str  | -           | 統合レイアウトへの転記対象外            |
"""

def generate_sample_data(num_records=10):
    data = []
    
    for i in range(num_records):
        report_date = datetime.now() - timedelta(days=np.random.randint(0, 365))
        effective_date = report_date + timedelta(days=np.random.randint(1, 180))
        
        record = {
            "report_date": report_date.strftime("%m/%d"),  # MM/DD形式
            "application_number": i + 1,
            "effective_date": effective_date.strftime("%Y/%m/%d"),  # YYYY/MM/DD形式
            "application_type": np.random.choice(["新設", "変更", "廃止"]),
            "target_org": np.random.choice(["課・エリア", "中間階層"]),
            "branch_code": f"{np.random.randint(10000, 99999):05d}",
            "branch_name_ja": f"支店{np.random.randint(1, 100)}",
            "branch_name_en": f"Branch {np.random.randint(1, 100)}",
            "intermediate_level_code": f"IL{np.random.randint(100, 999):03d}",
            "intermediate_level_name_ja": f"中間階層{np.random.randint(1, 50)}",
            "intermediate_level_name_en": f"Intermediate Level {np.random.randint(1, 50)}",
            "intermediate_level_abbr_ja": f"中階{np.random.randint(1, 50)}",
            "intermediate_level_abbr_en": f"IL{np.random.randint(1, 50)}",
            "section_area_code": f"{np.random.randint(1000, 9999):04d}",
            "section_area_name_ja": f"部署{np.random.randint(1, 100)}",
            "section_area_name_en": f"Section {np.random.randint(1, 100)}",
            "section_area_abbr_ja": f"部{np.random.randint(1, 100)}",
            "section_area_abbr_en": f"Sec{np.random.randint(1, 100)}",
            "aaa_transfer_date": (effective_date - timedelta(days=np.random.randint(1, 15))).strftime("%Y/%m/%d"),
            "change_details": f"変更詳細{np.random.randint(1, 100)}"
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

# オプション: DataFrameをExcel/pickleファイルに保存
df.to_excel("tests/table/sample_国企申請.xlsx", index=False)
df.to_pickle('tests/table/kokuki.pkl')

# pickle file 読み込み確認
kokuki = TableSearcher('kokuki.pkl', 'tests/table/')
log_msg(f'\n\n{tabulate_dataframe(kokuki.df)}')
