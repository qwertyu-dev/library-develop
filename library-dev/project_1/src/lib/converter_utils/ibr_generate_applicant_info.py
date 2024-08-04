"""ファイルパスから申請部署を判定する"""
from pathlib import Path

def generate_applicant_info(file_path: str | Path) -> int:
    """申請者情報を生成する

    Function Overview:
        ファイル名に基づいて申請者情報を示す数値を生成します。
        この関数はpandasのDataFrameに対してベクトル処理で適用することを想定しています。

    Arguments:
        file_path (str | Path): 申請データファイルのフルパス

    Return Value:
        int: 申請者情報を示す数値 1: 人事, 2: 国企, 3: 関連(ダミー課あり), 4: 関連(ダミー課なし)

    Usage Example:
        >>> file_path = '/path/to/人事/申請データ.xlsx'
        >>> df = pd.read_excel(file_path)
        >>> applicant_info = generate_applicant_info(file_path)
        >>> df = df.assign(applicant_info=applicant_info)
        >>> print(df)
            その他のカラム      applicant_info
        0           データ1               1
        1           データ2               1
        2           データ3               1

    Algorithm:
        1. 入力されたファイルパスからファイル名を抽出
        2. ファイル名に特定の文字列が含まれているかを確認
        3. 条件に基づいて対応する数値を返す

    Exception:
        ValueError: ファイルパスが指定されていない場合、または不正なファイル名パターンの場合に発生

    Notes:
        - この関数は呼び出し元の条件判断に基づいて使用されることを想定しています
        - ファイル名の判定は大文字小文字を区別しません
        - pandas DataFrameに対してベクトル処理で適用することを推奨します
        - 利用局面としてassignメソッドを使用してDataFrameに固定値でColumnを差し込みを想定します

    Dependency:
        - pathlib
        - pandas

    ResourceLocation:
        - 本体:
            - src/utils/applicant_info_generator.py
        - テストコード:
            - tests/utils/test_applicant_info_generator.py

    Todo:
        - より詳細なファイル名パターンの検証を追加する
        - 新しい申請者タイプに対応できるよう拡張性を向上させる
        - パフォーマンス最適化のためにnumpy等を使用したさらなる高速化を検討する

    Change History:
    | No  | 修正理由                   | 修正点                           | 対応日     | 担当         |
    |-----|----------------------------|----------------------------------|------------|--------------|
    | v0.1| 初期定義作成               | 新規作成                         | 2024/08/04 | xxxx aaa.bbb |

    """
    if not file_path:
        err_msg = "ファイルパスが指定されていません"
        raise ValueError(err_msg) from None

    path = Path(file_path)
    file_name = path.name.lower()

    # 変換定義
    # 変動要素は当面ない状況、直接記載
    applicant_types = {
        "人事": 1,
        "国企": 2,
        "関連(ダミー課あり)": 3,
        "関連(ダミー課なし)": 4,
    }

    for key, value in applicant_types.items():
        if key in file_name:
            return value

    err_msg = f"不正なファイル名パターン: {file_name}"
    raise ValueError(err_msg) from None

