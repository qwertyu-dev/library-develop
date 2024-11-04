import pickle
import random
import sys
from datetime import datetime, timedelta
from io import StringIO
from pathlib import Path
from typing import List
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
| No | Column名称(日本語) | column_name(python) | 属性 | 桁数/文字数 | Column説明(略) |
|---:|:-------------------|:--------------------|:-----|:------------|:---------------|
| 1 | リファレンスDB反映日時 | reference_db_update_datetime | datetime | - | - |
| 2 | 組織変更反映日 | organization_change_date | str | - | 共通認証受渡予定日をYYYMMDD形式に変換したもの |
| 3 | 起因申請明細ID | ulid | str | - | 起因申請のULID |
| 4 | 部店コード(BPR) | branch_code_bpr | str | - | BPRシステムで使う部店コード |
| 5 | 部店名(BPR) | branch_name_bpr | str | - | BPRシステムで使う部店名称 |
| 6 | 課Gコード(BPR) | section_gr_code_bpr | str | - | BPRシステムで使う課Grコード |
| 7 | 課Gr名(BPR) | section_gr_name_bpr | str | - | BPRシステムで使う課Gr名称 |
| 8 | 部門コード(BPR) | business_unit_code_bpr | str | - | BPRシステムで使う部門コード |
| 9 | 親部店コード | parent_branch_code | str | - | 共通認証への受渡し対象外 |
| 10 | 拠点内営業部コード | internal_sales_dept_code | str | - | 共通認証への受渡し対象外 |
| 11 | 拠点内営業部名称 | internal_sales_dept_name | str | - | 共通認証への受渡し対象外 |
| 12 | 部店コード(人事) | branch_code_jinji | str | - | 人事システムで管理している部店コード |
| 13 | 部店名(人事) | branch_name_jinji | str | - | 人事システムで管理している部店名称 |
| 14 | 課Grコード(人事) | section_gr_code_jinji | str | - | 人事システムで管理している課Grコード |
| 15 | 課Gr名(人事) | section_gr_name_jinji | str | - | 人事システムで管理している課Gr名称 |
| 16 | 部店コード(エリア) | branch_code_area | str | - | エリア情報として管理している部店コード |
| 17 | 部店名(エリア) | branch_name_area | str | - | エリア情報として管理している部店名称 |
| 18 | 課Grコード(エリア) | section_gr_code_area | str | - | エリア情報として管理している課Grコード |
| 19 | 課Gr名(エリア) | section_gr_name_area | str | - | エリア情報として管理している課Gr名称 |
| 20 | 出張所コード | sub_branch_code | str | - | 出張所・ローン推進室の場合に設定 |
| 21 | 出張所名称 | sub_branch_name | str | - | 出張所・ローン推進室の場合に設定 |
| 22 | 業務コード | business_code | str | - | エリアの場合に設定 |
| 23 | エリアコード | area_code | str | - | エリアの場合に設定 |
| 24 | エリア名称 | area_name | str | - | エリアの場合に設定 |
| 25 | 常駐部店コード | resident_branch_code | str | - | エリアの場合に設定 |
| 26 | 常駐部店名称 | resident_branch_name | str | - | エリアの場合に設定 |
| 27 | ポータル使用 | portal_use | str | - | - |
| 28 | ポータル送信 | portal_send | str | - | - |
| 29 | 本部/営業店フラグ | hq_sales_branch_flag | str | - | - |
| 30 | 組織分類 | organization_classification | str | - | - |
| 31 | 組織分類コード | organization_classification_code | str | - | - |
| 32 | 部店ソート番号 | branch_sort_number | str | - | - |
| 33 | 部店ソート番号2 | branch_sort_number2 | str | - | - |
| 34 | カナ組織名(カナ) | organization_name_kana | str | - | - |
| 35 | DPコード | dp_code | str | - | ファイルサーバのドライブの設定に使用 |
| 36 | DPコード(行員外) | dp_code_bp | str | - | ファイルサーバのOドライブの設定に使用 |
| 37 | GRコード | gr_code | str | - | ファイルサーバのQドライブの設定に使用 |
| 38 | GRコード(行員外) | gr_code_bp | str | - | ファイルサーバのQドライブの設定に使用 |
| 39 | GRPSコード | grps_code | str | - | - |
| 40 | BPR対象/対象外フラグ | bpr_target_flag | str | - | BPR・AD対象:1、ADのみ対象:2、BPR・AD対象外:0 |
| 41 | 出向リカバリフラグ | secondment_recovery_flag | str | - | 出向中に行員IDでBPRを使用できるようにするためのフラグ。特定の関連会社でONとなる |
| 42 | 備考 | remarks | str | - | - |
| 43 | SortEn | sort | str | - | 10で固定 |
| 44 | 組織変更情報 | organization_change_info | str | - | - |
| 45 | 支社内法人部コード | corporate_division_code | str | - | ブランクで固定 |
| 46 | 課Grソート番号 | section_gr_sort_number | str | - | ブランクで固定 |
| 47 | メールサーバ | mail_server | str | - | ブランクで固定 |
| 48 | 全行サーバ | bank_wide_server | str | - | ブランクで固定 |
| 49 | 部店サーバ(DBサーバ) | branch_server | str | - | ブランクで固定 |
| 50 | 部店のグループ名 | branch_group_name | str | - | ブランクで固定 |
| 51 | AD使用フラグ | ad_use_flag | str | - | 10で固定 |
| 52 | ADサーバ | ad_server | str | - | ブランクで固定 |
| 53 | ADドメイン | ad_domain | str | - | ブランクで固定 |
| 54 | 特別ドメインフラグ | special_domain_flag | str | - | ブランクで固定 |
| 55 | ホームディレクトリドライブ | home_directory_drive | str | - | ブランクで固定 |
| 56 | 行員特別ドメイン名 | employee_special_domain_name | str | - | ブランクで固定 |
| 57 | 対象会社コード | target_company_code | str | - | ブランクで固定 |
| 58 | 対象会社ドメイン名 | target_company_domain_name | str | - | ブランクで固定 |
| 59 | サブドメインあり会社ドメイン名 | company_domain_with_subdomain | str | - | ブランクで固定 |
| 60 | サブドメインなし会社ドメイン名 | company_domain_without_subdomain | str | - | ブランクで固定 |
| 61 | 予備1 | reserved1 | str | - | ブランクで固定 |
| 62 | 予備2 | reserved2 | str | - | ブランクで固定 |
| 63 | 予備3 | reserved3 | str | - | ブランクで固定 |
| 64 | 予備4 | reserved4 | str | - | ブランクで固定 |
| 65 | 予備5 | reserved5 | str | - | ブランクで固定 |
| 66 | 予備6 | reserved6 | str | - | ブランクで固定 |
| 67 | 予備7 | reserved7 | str | - | ブランクで固定 |
| 68 | 予備8 | reserved8 | str | - | ブランクで固定 |
| 69 | 予備9 | reserved9 | str | - | ブランクで固定 |
| 70 | 予備10 | reserved10 | str | - | ブランクで固定 |
"""
def generate_branch_code(index: int, branch_type: str = 'HQ') -> str:
    """Generate branch code based on type and rules"""
    if branch_type == 'HQ':  # 本部
        return f'6{str(index).zfill(3)}0'
    elif branch_type == 'DOMESTIC':  # 国内支店
        return f'0{str(index).zfill(3)}0'
    elif branch_type == 'CORPORATE':  # 法人営業
        return f'1{str(index).zfill(3)}0'
    elif branch_type == 'OVERSEAS':  # 海外拠点
        return f'3{str(index).zfill(3)}0'
    else:
        return f'7{str(index).zfill(3)}0'  # 関連会社

def generate_section_gr_code(branch_code: str, is_regular: bool = True) -> str:
    """Generate section group code based on rules"""
    if not is_regular:
        return random.choice(['93000', '95000'])  # 休職・本部詰
    base = branch_code[:4]
    return f'{base}{random.randint(1, 9)}'

def generate_sample_data(num_records: int = 10) -> pd.DataFrame:
    """Generate sample reference table data"""
    
    # Initialize lists for each column
    records = []
    
    # Generate base branch types
    branch_types = ['HQ', 'DOMESTIC', 'CORPORATE', 'OVERSEAS', 'AFFILIATE']
    weights = [0.3, 0.3, 0.2, 0.1, 0.1]  # Adjust weights to match real-world distribution
    
    current_date = datetime.now()
    
    for i in range(num_records):
        branch_type = random.choices(branch_types, weights=weights)[0]
        branch_code_bpr = generate_branch_code(i + 1, branch_type)
        is_regular = random.random() > 0.1  # 10% chance for 休職・本部詰
        
        record = {
            'reference_db_update_datetime': current_date + timedelta(days=random.randint(0, 30)),
            'organization_change_date': (current_date + timedelta(days=random.randint(1, 60))).strftime('%Y%m%d'),
            'ulid': f'ULID{str(i).zfill(6)}',
            
            # BPR related fields
            'branch_code_bpr': branch_code_bpr,
            'branch_name_bpr': f'支店{i+1}' if branch_type == 'DOMESTIC' else f'部署{i+1}',
            'section_gr_code_bpr': generate_section_gr_code(branch_code_bpr, is_regular),
            'section_gr_name_bpr': f'グループ{i+1}',
            'business_unit_code_bpr': str(random.randint(1, 9)),
            
            # Parent and internal codes
            'parent_branch_code': generate_branch_code(i // 2, branch_type),  # Reuse to ensure parent-child relationship
            'internal_sales_dept_code': f'S{str(i).zfill(4)}' if branch_type == 'DOMESTIC' else '',
            'internal_sales_dept_name': f'営業部{i+1}' if branch_type == 'DOMESTIC' else '',
            
            # Human resources (Jinji) related fields
            'branch_code_jinji': branch_code_bpr,  # Usually same as BPR
            'branch_name_jinji': f'支店{i+1}' if branch_type == 'DOMESTIC' else f'部署{i+1}',
            'section_gr_code_jinji': generate_section_gr_code(branch_code_bpr, is_regular),
            'section_gr_name_jinji': f'グループ{i+1}',
            
            # Area related fields
            'branch_code_area': branch_code_bpr,  # Usually same as BPR
            'branch_name_area': f'支店{i+1}' if branch_type == 'DOMESTIC' else f'部署{i+1}',
            'section_gr_code_area': generate_section_gr_code(branch_code_bpr, is_regular),
            'section_gr_name_area': f'グループ{i+1}',
            
            # Sub-branch related fields
            'sub_branch_code': f'SB{str(i).zfill(3)}' if branch_type == 'DOMESTIC' else '',
            'sub_branch_name': f'出張所{i+1}' if branch_type == 'DOMESTIC' else '',
            
            # Area specific fields
            'business_code': f'B{str(i).zfill(3)}',
            'area_code': f'A{str(i).zfill(3)}',
            'area_name': f'エリア{i+1}',
            'resident_branch_code': generate_branch_code(i % 5, 'DOMESTIC'),
            'resident_branch_name': f'常駐支店{i+1}',
            
            # System flags and settings
            'portal_use': random.choice(['0', '1']),
            'portal_send': random.choice(['0', '1']),
            'hq_sales_branch_flag': '1' if branch_type == 'HQ' else '0',
            'organization_classification': branch_type,
            'organization_classification_code': str(random.randint(1, 5)),
            'branch_sort_number': str(i+1).zfill(4),
            'branch_sort_number2': str(i+1).zfill(4),
            'organization_name_kana': f'シテン{i+1}' if branch_type == 'DOMESTIC' else f'ブショ{i+1}',
            
            # Drive and system codes
            'dp_code': f'DP{str(i).zfill(3)}',
            'dp_code_bp': f'DPB{str(i).zfill(3)}',
            'gr_code': f'GR{str(i).zfill(3)}',
            'gr_code_bp': f'GRB{str(i).zfill(3)}',
            'grps_code': f'GRPS{str(i).zfill(3)}',
            
            # Flags
            'bpr_target_flag': random.choice(['0', '1', '2']),
            'secondment_recovery_flag': '1' if branch_type == 'AFFILIATE' else '0',
            'remarks': f'備考{i+1}',
            
            # Fixed values
            'sort': '10',
            'organization_change_info': '',
            'corporate_division_code': '',
            'section_gr_sort_number': '',
            'mail_server': '',
            'bank_wide_server': '',
            'branch_server': '',
            'branch_group_name': '',
            'ad_use_flag': '10',
            'ad_server': '',
            'ad_domain': '',
            'special_domain_flag': '',
            'home_directory_drive': '',
            'employee_special_domain_name': '',
            'target_company_code': '',
            'target_company_domain_name': '',
            'company_domain_with_subdomain': '',
            'company_domain_without_subdomain': '',
        }
        
        # Add reserved fields
        for i in range(1, 11):
            record[f'reserved{i}'] = ''
            
        records.append(record)
    
    # Create DataFrame
    df = pd.DataFrame(records)
    
    return df


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
df.to_excel("tests/table/sample_リファレンステーブル.xlsx", index=False)
df.to_pickle('tests/table/reference_table.pkl')

# pickle file 読み込み確認
reference = TableSearcher('reference_table.pkl', 'tests/table/')
log_msg(f'\n\n{tabulate_dataframe(reference.df)}')
log_msg(f'\n\n{reference.df.columns.to_numpy()}')

########################################################################
@pytest.fixture(scope="session")
def temp_data_dir(tmp_path_factory) -> Path:
    """Create a temporary directory for test data"""
    return tmp_path_factory.mktemp("test_data")

@pytest.fixture(scope="function")
def reference_table_from_docstring(temp_data_dir) -> pd.DataFrame:
    """Load reference table data from docstring"""
    docstring = """
    # ここにExcelからコピーしたデータを貼り付ける
    """
    if docstring.isspace():
        return pd.DataFrame()

    return pd.read_csv(
        StringIO(docstring),
        header=0,
        sep=r'\s+',
        dtype='object',
    )

@pytest.fixture(scope="function")
def reference_table_from_docstring_testdata_nnn(temp_data_dir) -> pd.DataFrame:
    """Load reference table data from docstring"""
    docstring = """
    # ここにExcelからコピーしたデータを貼り付ける
    """
    if docstring.isspace():
        return pd.DataFrame()

    _df = pd.read_csv(
        StringIO(docstring),
        header=0,
        sep=r'\s+',
        dtype='object',
    )
    file_name = 'reference_table_testdata_nnn.pkl'
    pickle_file_path = Path(temp_data_dir) / file_name
    _df.to_pickle(pickle_file_path)

    # 利用方法
    # reference = TableSearcher('reference_table_testdata_nnn.pkl', pickle_file_path)

    return _df
