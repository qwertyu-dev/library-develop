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

def generate_sample_data(num_records=10) -> pd.DataFrame:
    """レイアウトに従ってサンプルデータを生成する関数
    
    Args:
        num_records (int): 生成するレコード数。デフォルトは10。
    
    Returns:
        pd.DataFrame: 生成されたサンプルデータ
    """
    data = []
    
    # 部店コード帯域のリスト（先頭1桁で分類）
    branch_code_prefixes = {
        '0': '国内支店',
        '1': '国内法人営業拠点',
        '2': 'ローン推進部',
        '3': '海外拠点',
        '6': '銀行本部',
        '7': '関連会社',
        '9': '寮'
    }
    
    for _ in range(num_records):
        # 部店コードの生成
        prefix = np.random.choice(list(branch_code_prefixes.keys()))
        branch_code = f"{prefix}{np.random.randint(1000, 9999):04d}"
        
        # BPR対象/対象外フラグの生成（条件に基づく）
        bpr_target_flag = "1" if prefix not in ['7', '9'] else "0"
        
        # 共通認証受渡予定日の生成（現在日付から1年以内）
        auth_transfer_date = datetime.now() + timedelta(days=np.random.randint(1, 365))
        
        record = {
            "ulid": str(ulid.new()),
            "branch_code": branch_code,
            "branch_name": f"{branch_code_prefixes[prefix]}{np.random.randint(1, 100)}",
            "section_gr_code": f"{np.random.randint(10000, 99999):05d}",
            "section_gr_name": f"部署{np.random.randint(1, 100)}",
            "internal_sales_dept_code": f"{np.random.randint(0, 9999):04d}" if np.random.random() < 0.3 else "",
            "internal_sales_dept_name": f"営業部{np.random.randint(1, 100)}" if np.random.random() < 0.3 else "",
            "business_and_area_code": f"{np.random.randint(10000, 99999):05d}" if np.random.random() < 0.3 else "",
            "business_and_area_name": f"エリア{np.random.randint(1, 100)}" if np.random.random() < 0.3 else "",
            "resident_branch_code": f"{np.random.randint(10000, 99999):05d}" if np.random.random() < 0.3 else "",
            "resident_branch_name": f"常駐支店{np.random.randint(1, 100)}" if np.random.random() < 0.3 else "",
            "form_type": np.random.choice(["1", "2", "3", "4"]),  # 1:人事, 2:国際事務企画室, 3:関連会社, 4:関連ダミー課Gr
            "application_type": np.random.choice(["新設", "変更", "廃止"]),
            "target_org": np.random.choice([
                "部店", "課", "エリア", "拠点内営業部",
                "課/エリア", "課/エリア(拠点内営業部)"
            ]),
            "business_unit_code_bpr": f"{np.random.randint(100, 999):03d}",
            "parent_branch_code": f"{np.random.randint(10000, 99999):05d}" if np.random.random() < 0.8 else "",
            "branch_name_kana": f"シテン{np.random.randint(1, 100)}",
            "section_name_en": f"Department {np.random.randint(1, 100)}",
            "section_name_kana": f"カナブモン{np.random.randint(1, 100)}",
            "section_name_abbr": f"部{np.random.randint(1, 100)}",
            "bpr_target_flag": bpr_target_flag,
            "auth_transfer_date": auth_transfer_date,
            "remarks": f"備考{np.random.randint(1, 100)}",
            "debug_apply_facade_name": f"Facade{np.random.randint(1, 100)}"
        }
        data.append(record)

    df = pd.DataFrame(data)

    # データ型の調整
    df['auth_transfer_date'] = pd.to_datetime(df['auth_transfer_date'])

    return df

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
df.to_excel("tests/table/sample_受付.xlsx", index=False)
df.to_pickle('tests/table/preparation_output_layout.pkl')

# pickle file 読み込み確認
preparation = TableSearcher('preparation_output.pkl', 'tests/table/')
log_msg(f'\n\n{tabulate_dataframe(preparation.df)}')
