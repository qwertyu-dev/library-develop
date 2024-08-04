"""人事部部門コードからBPR部門コードへの変換"""
import pandas as pd
from pathlib import Path

class BusinessUnitCodeConverter:
    """人事部門コードの変換を行うクラス

    ClassOverView:
    - 人事部門コードをキーとして、変換テーブルから対応する主管部門コード及びBPR部門コードを取得する

    Attributes:
    - conversion_table (pd.DataFrame): 変換テーブル
        - 人事部門コードをキーとして持ち、変換対応する情報を含むDataFrame
        - pickleからロードした部門変換テーブル実体

    Notes:
    - 変換テーブルは business_unit_code_table.pickle ファイルから読み込まれるため、ファイルが存在し、pickle形式で保存されている必要がある
    - ファイルパスが間違っている場合、FileNotFoundErrorを発生する
    - 引数指定した人事部門コードが変換テーブルに存在しない場合、ValueErrorを返す
    - 予期せぬエラーが発生した場合、Exceptionを返す

    Dependency:
    - pickle
    - pandas
    - pathlib
    """

    def __init__(self, conversion_table_file: Path) -> None:
        """コンストラクタ

        - pickle ファイルから変換テーブルを読み込みconversion_table 属性に格納する
        - ファイルパスの操作はpathlib.Pathを使用する

        Args:
            conversion_table_file (Path): 変換テーブルの pickle ファイルパス

        Raises:
            FileNotFoundError: ファイルが存在しない場合に発生する
            Exception: その他の予期せぬエラーが発生した場合
        """
        try:
            self.conversion_table = pd.read_pickle(conversion_table_file)
            self.conversion_table = self.conversion_table.set_index('business_unit_code_jinji')
        except FileNotFoundError as e:
            err_msg = f"変換テーブルファイルが見つかりません: {conversion_table_file}"
            raise FileNotFoundError(err_msg) from e
        except Exception as e:
            err_msg = f"変換テーブルの読み込み中にエラーが発生しました: {str(e)}"
            raise Exception(err_msg) from e

    def get_business_unit_code_main(self, business_unit_code_jinji: str) -> str:
        """人事部門コードから主管部門コードを取得する

        Args:
            business_unit_code_jinji (str): 人事部門コード

        Returns:
            str: 対応する主管部門コード

        Raises:
            ValueError: 指定コードが部門コード変換テーブル.人事部門コードに存在しない場合に発生する
            Exception: その他の予期せぬエラーが発生した場合
        """
        if business_unit_code_jinji not in self.conversion_table.index:
            err_msg = f"指定された人事部門コードは変換テーブルに存在しません: {business_unit_code_jinji}"
            raise ValueError(err_msg) from None

        try:
            return self.conversion_table.loc[business_unit_code_jinji, 'main_business_unit_code_jinji']
        except Exception as e:
            err_msg = f"主管部門コードの取得中にエラーが発生しました: {e}"
            raise Exception(err_msg) from e

    def get_business_unit_code_bpr(self, business_unit_code_jinji: str) -> str:
        """人事部門コードからBPR部門コードを取得する。

        Args:
            business_unit_code_jinji (str): 人事部門コード

        Returns:
            str: 対応するBPR部門コード

        Raises:
            ValueError: 指定コードが部門コード変換テーブル.人事部門コードに存在しない場合に発生する
            Exception: その他の予期せぬエラーが発生した場合
        """
        if business_unit_code_jinji not in self.conversion_table.index:
            err_msg = f"指定された人事部門コードは変換テーブルに存在しません: {business_unit_code_jinji}"
            raise ValueError(err_msg)

        try:
            return self.conversion_table.loc[business_unit_code_jinji, 'business_unit_code_bpr']
        except Exception as e:
            err_msg = f"BPR部門コードの取得中にエラーが発生しました: {e}"
            raise Exception(err_msg) from e
