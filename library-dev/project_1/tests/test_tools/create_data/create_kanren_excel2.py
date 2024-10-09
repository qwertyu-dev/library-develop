import random
import sys
from datetime import datetime, timedelta
from typing import Dict, List, Optional

import pandas as pd
import pytest
from pathlib import Path

from src.lib.common_utils.ibr_dataframe_helper import tabulate_dataframe
from src.lib.common_utils.ibr_decorator_config import initialize_config
from src.lib.common_utils.ibr_enums import LogLevel
from src.lib.common_utils.ibr_logger_helper import format_config

config = initialize_config(sys.modules[__name__])
log_msg = config.log_message

# Column定義取得
mapping = config.package_config['excel_definition_mapping_kanren']
log_msg(f"\n\n{format_config(mapping)}", LogLevel.INFO)

def generate_random_date(start_year: int = 2023, end_year: int = 2023) -> str:
    start_date = datetime(start_year, 1, 1)
    end_date = datetime(end_year, 12, 31)
    time_between_dates = end_date - start_date
    days_between_dates = time_between_dates.days
    random_number_of_days = random.randrange(days_between_dates)
    random_date = start_date + timedelta(days=random_number_of_days)
    return random_date.strftime("%Y-%m-%d")

def generate_random_data(include_errors: bool = False) -> Dict[str, str]:
    branch_number = random.randint(1, 50)
    section_number = random.randint(1, 20)
    data = {
        'application_type': random.choice(['新規', '変更', '削除']),
        'business_unit_code': f"BU{random.randint(100, 999)}",
        'parent_branch_code': f"PB{random.randint(100, 999)}",
        'branch_code': f"BR{random.randint(1000, 9999)}",
        'branch_name': f"関連会社支店{branch_number}",
        'section_gr_code': f"SG{random.randint(100, 999)}",
        'section_gr_name': f"課グループ{section_number}",
        'section_name_en': f"Section Group {section_number}",
        'aaa_transfer_date': generate_random_date(),
        'section_name_kana': f"カグループ{section_number}",
        'section_name_abbr': f"課G{section_number}",
        'bpr_target_flag': random.choice(['対象', '対象外'])
    }
    
    if include_errors and random.random() < 0.2:  # 20%の確率でエラーデータを含める
        error_field = random.choice(list(data.keys()))
        data[error_field] = ''  # エラーとして空文字を設定
    
    return data

def generate_test_data(num_rows: int = 5, include_errors: bool = False, seed: Optional[int] = None) -> pd.DataFrame:
    if seed is not None:
        random.seed(seed)
    
    data = [generate_random_data(include_errors) for _ in range(num_rows)]
    df = pd.DataFrame(data)
    df.rename(columns={v: k for k, v in mapping.items()}, inplace=True)
    return df

def save_to_excel(df: pd.DataFrame, file_name: str = "関連一括申請.xlsx") -> None:
    #excel_file_dir = config.common_config.get('optional_path', {}).get('SHARE_RECEIVE_PATH', '')
    #excel_file = Path(excel_file_dir) / file_name
    #try:
    #    df.to_excel(excel_file, index=False, engine='openpyxl')
    #    log_msg(f"File saved successfully: {excel_file}", LogLevel.INFO)
    #except Exception as e:
    #    log_msg(f"Error saving file: {e}", LogLevel.ERROR)

    excel_file_dir = config.common_config.get('optional_path', {}).get('SHARE_RECEIVE_PATH', '')
    base_excel_file_name =  config.package_config.get('excel_definition', []).get('UPDATE_RECORD_KANREN','')
    # ファイル名のパターンから実際のファイル名を生成
    base_name = base_excel_file_name.replace('*',f"_{datetime.now().strftime('%Y%m%d')}")
    file_name = f"{base_name[:-5]}.xlsx"
    excel_file = Path(excel_file_dir) / file_name
    sheet_name = config.package_config.get('excel_definition', []).get('UPDATE_RECORD_KANREN_SHEET_NAME','')

    try:
        with pd.ExcelWriter(excel_file, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name=sheet_name, index=False)
        log_msg(f"File saved successfully: {excel_file}", LogLevel.INFO)
    except Exception as e:
        log_msg(f"Error saving file: {e}", LogLevel.ERROR)

if __name__ == "__main__":
    # 正常系データ生成
    df_normal = generate_test_data(num_rows=5, seed=42)
    log_msg(f'\n\n正常系データ:\n{tabulate_dataframe(df_normal)}', LogLevel.INFO)
    save_to_excel(df_normal, "関連一括申請_正常系.xlsx")

    ## エラーを含むデータ生成
    #df_with_errors = generate_test_data(num_rows=10, include_errors=True, seed=43)
    #log_msg(f'\n\nエラーを含むデータ:\n{tabulate_dataframe(df_with_errors)}', LogLevel.INFO)
    #save_to_excel(df_with_errors, "関連一括申請_エラー含む.xlsx")

    ## 境界値テスト用データ生成（例：最大長の文字列）
    #df_boundary = generate_test_data(num_rows=1, seed=44)
    #df_boundary['branch_name'] = 'あ' * 100  # 例：支店名の最大長を100文字と仮定
    #log_msg(f'\n\n境界値テスト用データ:\n{tabulate_dataframe(df_boundary)}', LogLevel.INFO)
    #save_to_excel(df_boundary, "関連一括申請_境界値.xlsx")
