"""部署名をブランク分割する"""

import re

def format_department_name(department_name: str) -> str:
    r"""部署名を標準的な形式に整形する

    Function Overview:
        この関数は、入力された部署名を一定のルールに従って整形します。
        特定の例外ケースを考慮し、「部」の後にスペースを挿入したり、
        特定のパターンでスペースを調整したりします。

    Arguments:
        department_name (str): 整形する部署名

    Return Value:
        str: 整形された部署名

    Usage Example:
        >>> format_department_name("営業本部業務部")
        "営業本部業務部"
        >>> format_department_name("システム部門")
        "システム部 門"

    Algorithm:
        1. 個別要件リストと例外ケースをチェック
            - 完全一致する場合は、そのまま返す

        2. 「〜部(拠点名)」パターンをチェック
            - このパターンに一致する場合は、そのまま返す

        3. 括弧内外で部署名を分割
            - 正規表現 r'(\([^)]*\))' を使用
            - 例: "システム部(東京)" → ["システム部", "(東京)"]

        4. 括弧の外側の部分に対して以下の処理を行う:
            a. 「部」の後にスペースを挿入
                - 「部」で終わる場合を除く
                - 例: "システム部門" → "システム部 門"

            b. 特定のパターンでスペースを調整
                - "部 部 " → "部部 "
                - "部 門" → "部門"
                - "部部門" → "部 部門"
                - "部門 (" → "部門("
                - "部 ·" → "部·"

        5. 分割した部分を再結合

        6. 部分マッチの例外処理
            - 特定のキーワード("中部", "春日部"など)の後のスペースを削除

        7. 先頭と末尾の余分なスペースを削除して結果を返す

    Exception:
        この関数は例外を発生させません。

    Notes:
        - 括弧内の文字列は処理されません。
        - 部署名の()出現パターンに依存した実装になっているため括弧の使用パターンが変更された場合は修正が必要です。

    Dependency:
        - re モジュール

    ResourceLocation:
        - 本体:
            - src/lib/converter_utils/ibr_department_formatter.py
        - テストコード:
            - tests/lib/converter_utils/ibr_department_formatter.py

    Todo:
        - より柔軟な括弧処理の実装
        - パフォーマンス最適化

    Change History:
    | No   | 修正理由     | 修正点   | 対応日     | 担当          |
    |------|--------------|----------|------------|---------------|
    | v0.1 | 初期定義作成 | 新規作成 | 2024/07/20 | xxxx aaa.bbb  |

    """
    # 個別要件リスト 完全一致でバイパス
    individual_requirements = [
        "営業本部業務部",
        "内部監査部業務監査グループ第三ユニット",
        "成田加良部社宅（６９１０）人事室",
        "葉山倶楽部（６９１０）人事室",
        "軽井沢倶楽部（６９１０）人事室",
    ]

    # 全体マッチの例外ケース 完全一致でバイパス
    full_match_exceptions = [
        "本部審議役",
        "本部審議役（大阪）",
        "本部審議役（名古屋）",
        "本部賛事役",
        "本部賛事役（大阪）",
        "本部賛事役（名古屋）",
    ]

    # 部分マッチの例外ケース 部分一致で処理
    partial_match_exceptions = [
        "中部",
        "東部",
        "西部",
        "春日部",
        "宇部",
        "内部",
    ]

    # 個別要件チェック
    if department_name in individual_requirements:
        return department_name

    # 全体マッチの例外チェック
    if department_name in full_match_exceptions:
        return department_name

    # 「〜部(拠点名)」パターンのチェック
    if re.search(r'部\([^)]*\)$', department_name):
        return department_name

    # 括弧内の処理を避けるため、括弧内外で分割
    parts = re.split(r'(\([^)]*\))', department_name)

    # 括弧の外側の部分のみ処理
    for i in range(0, len(parts), 2):
        # 「部」の後にスペースを挿入(最後の「部」を除く)
        # 否定先読み?!を適用しカッコ内のパターンに一致しない場合のみ
        # その位置でマッチする
        parts[i] = re.sub(r'部(?!$)', '部 ', parts[i])

        # ブランク戻しパターン
        parts[i] = parts[i].replace("部 部 ", "部部 ")
        parts[i] = parts[i].replace("部 門", "部門")
        parts[i] = parts[i].replace("部部門", "部 部門")
        parts[i] = parts[i].replace("部門 (", "部門(")
        parts[i] = parts[i].replace("部 ·", "部·")
        parts[i] = parts[i].replace("部 ・", "部・")

    department_name = ''.join(parts)

    # 部分マッチの例外処理 ブランク戻し
    for exception_case in partial_match_exceptions:
        if exception_case in department_name:
            department_name = department_name.replace(exception_case + " ", exception_case)

    return department_name.strip()
