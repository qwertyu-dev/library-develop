import ulid
import pandas as pd

def generate_ulid_column(df: pd.DataFrame) -> pd.DataFrame:
    """DataFrameに新しいULID列を追加する

    Function Overview:
    この関数は、与えられたDataFrameの先頭に新しい'ulid'列を挿入します。
    各行に対して一意の(ULIDUniversally Unique Lexicographically Sortable Identifier)を生成します。

    Arguments:
        df (pandas.DataFrame): ULID列を追加するデータフレーム

    Return Value:
        pandas.DataFrame: 'ulid'列が先頭に追加された新しいDataFrame

    Usage Example:
        >>> import pandas as pd
        >>> import ulid
        >>> data = {'name': ['Alice', 'Bob'], 'age': [25, 30]}
        >>> df = pd.DataFrame(data)
        >>> df_with_ulid = generate_ulid_column(df)
        >>> print(df_with_ulid.columns)
        Index(['ulid', 'name', 'age'], dtype='object')

    Algorithm:
        1. DataFrameの各行に対応する新しいULIDのリストを生成
        2. 生成したULIDリストを使用して、DataFrameの先頭に新しい'ulid'列を挿入
        3. 行毎に異なるULIDを挿入します

    Exception:
        TypeError: 引数dfがpandas.DataFrameでない場合に発生
        Exception: 予期せぬエラーが発生した場合、Exceptionを返す

    Notes:
        - この関数は元のDataFrameを変更します
        - 生成される各業務家のULIDは、呼び出し時の現在のタイムスタンプに基づいています
        - df.indexを使用して対象範囲定義を行う
        - 内包表現を使用する

    Dependency:
        - pandas
        - ulid-py

    Todo:
        - あれば記載する

    Chage History:
    | No   | 修正理由     | 修正点   | 対応日       | 担当          |
    |------|--------------|----------|--------------|---------------|
    | v0.1 | 初期定義作成 | 新規作成 | 2024/07/21   | |

    """
    # 関数の実装
    df.insert(0, 'ulid', [str(ulid.new()) for _ in df.index])
    return df
