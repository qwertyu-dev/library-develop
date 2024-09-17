import pandas as pd
import random
import datetime

# データ生成用の関数
def generate_random_data(column_name):
    if column_name == "報告日":
        return (datetime.datetime.now() - datetime.timedelta(days=random.randint(1, 30))).strftime("%Y-%m-%d")
    elif column_name in ["no", "部門コード", "親部店コード", "部店コード", "課/エリアコード", "常駐部店コード"]:
        return str(random.randint(1000, 99999))
    elif column_name in ["種類", "対象", "部店名称", "部店名称(英語)", "課/エリア名称", "課/エリア名称(英語)", "常駐部店名称", "備考"]:
        return ''.join(random.choices("ABCDEFGHIJKLMNOPQRSTUVWXYZ", k=random.randint(5, 15)))
    elif column_name in ["有効日付", "純新規店の組織情報受渡し予定日(開店日基準)", "共通認証受渡し予定日(人事データ反映基準)"]:
        return (datetime.datetime.now() + datetime.timedelta(days=random.randint(1, 180))).strftime("%Y-%m-%d")
    else:
        return None

# レイアウト定義
columns = [
    "報告日",
    "no",
    "有効日付",
    "種類",
    "対象",
    "部門コード",
    "親部店コード",
    "部店コード",
    "部店名称",
    "部店名称(英語)",
    "課/エリアコード",
    "課/エリア名称",
    "課/エリア名称(英語)",
    "常駐部店コード",
    "常駐部店名称",
    "純新規店の組織情報受渡し予定日(開店日基準)",
    "共通認証受渡し予定日(人事データ反映基準)",
    "備考",
]

# データフレームの作成
data = []
for i in range(50):
    row = [generate_random_data(column) for column in columns]
    data.append(row)

df = pd.DataFrame(data, columns=columns)

# Excelファイルへの出力 (Indexなし)
df.to_excel("jinji_requests.xlsx", index=False)

print("Excelファイルを作成しました: jinji_requests.xlsx")
