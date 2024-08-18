import pandas as pd
import numpy as np
from datetime import datetime, timedelta

def generate_sample_data(num_records=100):
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

# サンプルDataFrameの生成
df = generate_sample_data()

# 最初の数行と基本情報の表示
print(df.head())
print("\nDataFrameの情報:")
print(df.info())

# オプション：DataFrameをCSVファイルに保存
df.to_excel("sample_一括申請関連レイアウト.xlsx", index=False)