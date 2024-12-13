import re

def convert_japanese_symbols(text):
    # 変換ルールを定義
    conversion_rules = [
        # 会社形態
        (r'㈱|（株）|㊑', '（株）'),  # 株式会社
        (r'㈲|（有）', '（有）'),     # 有限会社
        (r'㈴|（名）', '（名）'),     # 合名会社
        (r'㈵|（特）', '（特）'),     # 特例有限会社
        (r'㈶|（財）', '（財）'),     # 財団法人
        (r'㈻|（学）', '（学）'),     # 学校法人
        (r'㈳|（社）', '（社）'),     # 社団法人
        (r'㈿|（協）', '（協）'),     # 協同組合
        (r'㈼|（監）', '（監）'),     # 監査法人
        (r'㈹|（代）', '（代）'),     # 代表
        (r'㈴|（名）', '（名）'),     # 合名会社
        (r'㈺|（資）', '（資）'),     # 合資会社
        (r'㈾|（合）', '（合）'),     # 合同会社
        (r'㈱|㍿', '株式会社'),       # 株式会社（末尾）


        # 元号
        (r'㍻', '平成'),              # 平成
        (r'㍼', '昭和'),              # 昭和
        (r'㍽', '大正'),              # 大正
        (r'㍾', '明治'),              # 明治
        (r'㋿', '令和'),              # 令和

        # 曜日と一般的な記号
        (r'㊊', '月'),                # 月曜日
        (r'㊋', '火'),                # 火曜日
        (r'㊌', '水'),                # 水曜日
        (r'㊍', '木'),                # 木曜日
        (r'㊎', '金'),                # 金曜日
        (r'㊏', '土'),                # 土曜日
        (r'㊐', '日'),                # 日曜日
        (r'㊗', '祝'),                # 祝日
        (r'㊙', '秘'),                # 秘密
        (r'㊞', '印'),                # 印鑑
        (r'㊤', '上'),                # 上
        (r'㊥', '中'),                # 中
        (r'㊦', '下'),                # 下
        (r'㊧', '左'),                # 左
        (r'㊨', '右'),                # 右
        (r'㊩', '医'),                # 医療
        (r'㊒', '祝'),                # 祝
        (r'㊔', '名'),                # 名
        (r'㊕', '特'),                # 特
        (r'㊖', '財'),                # 財
        (r'㊘', '労'),                # 労働
        (r'㊚', '男'),                # 男性
        (r'㊛', '女'),                # 女性
        (r'㊜', '適'),                # 適
        (r'㊝', '優'),                # 優
        (r'㊟', '注'),                # 注意
        (r'㊠', '項'),                # 項目
        (r'㊡', '休'),                # 休業
        (r'㊢', '写'),                # 写し
        (r'㊣', '正'),                # 正

        # その他の記号
        (r'№', 'No.'),               # ナンバー
        (r'℡', 'TEL'),               # 電話
    ]
    
    # 各ルールを適用
    for pattern, replacement in conversion_rules:
        text = re.sub(pattern, replacement, text)
    
    return text

# テスト用の文字列
test_strings = [
    "㈱山田商事は大阪にあります。㈲佐藤工業は東京です。",
    "㈴鈴木商店と㈵田中特殊工業が業務提携",
    "㈶日本文化振興財団 ㈳日本環境協会 ㈻東京大学",
    "㈿中央市場 ㈼山田会計事務所 ㈸高橋商事",
    "㈾テクノロジーソリューションズ ㈹鈴木一郎",
    "㍻5年創業 ㍼63年設立 ℡03-1234-5678",
    "㋿3年に設立された新しい会社です。",
    "㊊㊋㊌㊍㊎㊏㊐の全曜日営業、㊡日は㊠に注意",
    "㊚性社員と㊛性社員の㊘働環境改善に努めます",
    "㊙情報の取り扱いには㊟意が必要です",
    "㊤階から㊦階まで、㊧から㊨へ案内表示があります",
    "№1の企業を目指して㊗日も営業中"
]

# テスト実行
for string in test_strings:
    print("変換前:", string)
    print("変換後:", convert_japanese_symbols(string))
    print()