import pandas as pd
import numpy as np
from datetime import datetime, timedelta

def generate_sample_data(num_records=100):
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

# サンプルDataFrameの生成
df = generate_sample_data()

# 最初の数行と基本情報の表示
print(df.head())
print("\nDataFrameの情報:")
print(df.info())

# オプション：DataFrameをCSVファイルに保存
df.to_excel("sample_一括申請国企レイアウト.xlsx", index=False)