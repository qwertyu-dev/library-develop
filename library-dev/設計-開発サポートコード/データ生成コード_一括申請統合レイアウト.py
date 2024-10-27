import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import ulid

from tabulate import tabulate

"""
| No  | Column名称(日本語)         | column_name(python)                   | 属性 | 桁数/文字数 | Column説明(略)                                                                                              |
|----:|:---------------------------|:--------------------------------------|:-----|:------------|:------------------------------------------------------------------------------------------------------------|
|   1 | ULID                       | ulid                                  | str  | 26          | 明細毎にULIDを一意に設定                                                                                    |
|   2 | 申請元情報                 | form_type                             | str  | 1           | ファイル取り込み時に以下いずれかを設定<br>1: 人事提出ファイル<br>2: 国際事務企画室提出ファイル<br>3: 関連会社提出ファイル<br>4: 関連ダミー課Gr |
|   3 | 種類                       | application_type                      | str  | 1           | 新設/変更/廃止のいずれか                                                                                    |
|   4 | 対象                       | target_org                            | str  | 20          | 以下いずれかを設定<br>・部店、課、エリア、拠点内営業部<br>・課/エリア、課/エリア(拠点内営業部)              |
|   5 | 部門コード                 | business_unit_code                    | str  | 3           | -                                                                                                           |
|   6 | 親部店コード               | parent_branch_code                    | str  | 5           | -                                                                                                           |
|   7 | 部店コード                 | branch_code                           | str  | 5           | -                                                                                                           |
|   8 | 部店名称                   | branch_name                           | str  | 78          |  -                                                                                                          |
|   9 | 課Grコード                 | section_gr_code                       | str  | 5           |  -                                                                                                          |
|  10 | 課Gr名称                   | section_gr_name                       | str  | 48          |  -                                                                                                          |
|  11 | 課名称(英語)               | section_name_en                       | str  | 75          | -                                                                                                           |
|  12 | 常駐部店コード             | resident_branch_code                  | str  | 5           | -                                                                                                           |
|  13 | 常駐部店名称               | resident_branch_name                  | str  | 48          | -                                                                                                           |
|  14 | 共通認証受渡し予定日       | aaa_transfer_date                     | str  | 8           | -                                                                                                           |
|  15 | 拠点内営業部コード         | sales_department_code_within_location | str  | 5           | -                                                                                                           |
|  16 | 拠点内営業部名称           | sales_department_name_within_location | str  | 78          | -                                                                                                           |
|  17 | エリアコード               | area_code                             | str  | 5           | -                                                                                                           |
|  18 | エリア名称                 | area_name                             | str  | 48          | -                                                                                                           |
|  19 | 備考                       | remarks                               | str  | 100         | -                                                                                                           |
|  20 | 部店カナ                   | branch_name_kana                      | str  | 48          | -                                                                                                           |
|  21 | 課Gr名称(カナ)             | section_gr_name_kana                  | str  | 12          | -                                                                                                           |
|  22 | 課Gr名称(略称)             | section_gr_name_abbr                  | str  | 10          | -                                                                                                           |
|  23 | BPR対象/対象外フラグ       | bpr_target_flag                       | str  | 1           | -                                                                                                           |
"""
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from ulid import ULID

def generate_sample_data(num_records=100):
    data = []
    
    for _ in range(num_records):
        record = {
            "ulid": str(ulid.new()),
            "form_type": np.random.choice(["1", "2", "3", "4"]),
            "application_type": np.random.choice(["新設", "変更", "廃止"]),  # 1: 新設, 2: 変更, 3: 廃止
            "target_org": np.random.choice(["部店", "課", "エリア", "拠点内営業部", "課/エリア", "課/エリア(拠点内営業部)"]),
            "business_unit_code": f"{np.random.randint(100, 999):03d}",
            "parent_branch_code": f"{np.random.randint(10000, 99999):05d}",
            "branch_code": f"{np.random.randint(10000, 99999):05d}",
            "branch_name": f"支店{np.random.randint(1, 100)}".ljust(78),
            "section_gr_code": f"{np.random.randint(10000, 99999):05d}",
            "section_gr_name": f"部署{np.random.randint(1, 100)}".ljust(48),
            "section_name_en": f"Department {np.random.randint(1, 100)}".ljust(75),
            "resident_branch_code": f"{np.random.randint(10000, 99999):05d}",
            "resident_branch_name": f"常駐支店{np.random.randint(1, 100)}".ljust(48),
            "aaa_transfer_date": (datetime.now() + timedelta(days=np.random.randint(1, 365))).strftime("%Y%m%d"),
            "sales_department_code_within_location": f"{np.random.randint(0000, 9999):04d}",
            "sales_department_name_within_location": f"拠点内営業部名称.{np.random.randint(100, 999):03d}",
            "area_code": f"{np.random.randint(10000, 99999):05d}",
            "area_name": f"エリア{np.random.randint(1, 100)}".ljust(48),
            "remarks": f"備考{np.random.randint(1, 100)}".ljust(100),
            "branch_name_kana": "".ljust(48),
            "section_gr_name_kana": f"ブモン{np.random.randint(1, 100)}".ljust(12),
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
df.to_excel("sample_一括申請統合レイアウト.xlsx", index=False)
df.to_pickle('df_integrated_layout.pkl')

df_pickled = pd.read_pickle('df_integrated_layout.pkl')
print(df_pickled)