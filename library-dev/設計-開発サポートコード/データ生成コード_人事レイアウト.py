import pandas as pd
import numpy as np
from datetime import datetime, timedelta

def generate_sample_data(num_records=100):
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

# サンプルDataFrameの生成
df = generate_sample_data()

# 最初の数行と基本情報の表示
print(df.head())
print("\nDataFrameの情報:")
print(df.info())

# オプション：DataFrameをCSVファイルに保存
df.to_excel("sample_一括申請人事レイアウト.xlsx", index=False)