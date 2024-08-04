import pandas as pd
from pathlib import Path

class BusinessUnitCodeConverter:
    """人事部門コードの変換を行うクラス

    Class OverView:
        記載してください

    Attributes:
        記載してください

    Methods:
        記載してください

    Usage Example:
        >>> from pathlib import Path
        >>> converter = BusinessUnitCodeConverter(Path("business_unit_code_table.pickle"))
        >>> main_code = converter.get_business_unit_code_main("HR001")
        >>> print(main_code)
        MAIN001

        >>> bpr_code = converter.get_business_unit_code_bpr("HR001")
        >>> print(bpr_code)
        BPR001

    Notes:
        - 変換テーブルは business_unit_code_table.pickle ファイルから読み込まれるためファイルが存在し、pickle形式で正しく保存されている必要があります。
        - ファイルパスが間違っている場合、FileNotFoundErrorが発生します。
        - 指定した人事部門コードが変換テーブルに存在しない場合、ValueErrorが返されます。
        - 予期せぬエラーが発生した場合、Exceptionが返されます。

    Dependency:
        - pickle
        - pandas
        - pathlib


    ResourceLocation:
        - 本体
            - src/lib/convertor_utils/ibr_business_unit_code_converter.py
        - テストコード
            - tests/lib/convertor_utils/test_ibr_business_unit_code_converter.py

    Todo:
    - あれば記載する

    Change History:
    | No   | 修正理由     | 修正点           | 対応日     | 担当             |
    |------|--------------|------------------|------------|------------------|
    | v0.1 | 初期定義作成 | クラス全体の実装 | 2024/07/21 | |

    """

    def __init__(self, conversion_table_file: Path) -> None:
        """コンストラクタ

        Arguments:
        conversion_table_file (Path): 変換テーブルのpickleファイルパス
        """
        # 初期化処理

    def get_business_unit_code_main(self, : str) -> str:
        """人事部門コードから主管部門コードを取得する

        Arguments:
            (str): 人事部門コード

        Return Value:
            str: 対応する主管部門コード

        Exception:
            ValueError: 指定コードが部門コード変換テーブル.人事部門コードに存在しない場合に発生する
            Exception: その他の予期せぬエラーが発生した場合

        Usage Example:
            >>> converter = BusinessUnitCodeConverter(Path("business_unit_code_table.pickle"))
            >>> main_code = converter.get_business_unit_code_main("HR001")
            >>> print(main_code)
            MAIN001
        """
        # メソッドの実装
        pass

    def get_business_unit_code_bpr(self, : str) -> str:
        """人事部門コードからBPR部門コードを取得する

        Arguments:
            (str): 人事部門コード

        Return Value:
            str: 対応するBPR部門コード

        Exception:
            ValueError: 指定コードが部門コード変換テーブル.人事部門コードに存在しない場合に発生する
            Exception: その他の予期せぬエラーが発生した場合

        Usage Example:
            >>> converter = BusinessUnitCodeConverter(Path("business_unit_code_table.pickle"))
            >>> bpr_code = converter.get_business_unit_code_bpr("HR001")
            >>> print(bpr_code)
            BPR001
        """
        # メソッドの実装
        pass
