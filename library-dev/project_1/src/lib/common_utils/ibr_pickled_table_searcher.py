from cachetools import cached, TTLCache
from pathlib import Path
from typing import Callable
import os
import pandas as pd

class FileConfig:
    """デフォルト値定数定義"""
    DEFAULT_EXEC_PATTERN = 'src'
    TABLE_DIR_NAME = 'table'
    CACHE_MAXSIZE = 100
    CACHE_TTL = 3600

class TableSearcher:
    """テーブルデータの検索と情報取得を行うクラス

    Class Overview:
        このクラスは、pickleファイルとして保存されたテーブルデータを読み込み、
        様々な条件での検索機能を提供します。シンプルな検索と高度な検索の両方をサポートし、
        データの概要情報やカラム情報の取得も可能です。また、ファイルの更新を検知し、
        キャッシュを適切に管理します。

    Attributes:
        table_name (str): 検索対象のテーブル名(ファイル名)
        table_path (str): テーブルファイルのパス
        file_path (Path): テーブルファイルの完全パス
        last_modified_time (float): ファイルの最終更新時刻
        df (pd.DataFrame): 読み込まれたテーブルデータ
        is_updated (bool): データが最後の読み込み以降に更新されたかどうか

    Condition Information:
        - Condition:1
            - ID: SIMPLE_SEARCH
            - Type: 検索条件
            - Applicable Scenarios: カラム名と値の単純な一致、または前方一致での検索
        - Condition:2
            - ID: ADVANCED_SEARCH
            - Type: 検索条件
            - Applicable Scenarios: 複雑な条件や複数のカラムを組み合わせた検索

    Pattern Information:
        - Pattern:1
            - ID: AND_SEARCH
            - Type: 検索パターン
            - Applicable Scenarios: 複数の条件を全て満たすデータの検索
        - Pattern:2
            - ID: OR_SEARCH
            - Type: 検索パターン
            - Applicable Scenarios: 複数の条件のいずれかを満たすデータの検索

    Methods:
        __init__(table_name, file_path, df_loader, get_table_path, get_file_modified_time, load_table): コンストラクタ
        create_for_production(table_name): 本番環境用のインスタンスを作成
        create_for_test(table_name, mock_file_path, mock_df_loader, mock_get_table_path, mock_get_file_modified_time, mock_load_table): テスト用のインスタンスを作成
        _default_get_table_path(): デフォルトのテーブルパス取得メソッド
        _default_get_file_modified_time(): デフォルトのファイル更新時刻取得メソッド
        _should_update_cache(): キャッシュ更新の判断
        _default_load_table(): デフォルトのテーブル読み込みメソッド
        refresh_data(): データの強制再読み込み
        simple_search(conditions, operator): シンプルな条件での検索
        advanced_search(condition_func): 高度な条件での検索

    Usage Example:
        >>> searcher = TableSearcher("example_table.pkl")
        >>> result = searcher.simple_search({"column1": "value1", "column2": "startswith:prefix"}, operator='AND')
        >>> print(result)

    Notes:
        - テーブルデータはpickle形式で保存されている必要があります
        - 大規模なデータセットの場合、メモリ使用量に注意してください
        - ファイルの更新を検知し、自動的にキャッシュを更新します

    Dependency:
        - pandas
        - pathlib
        - os
        - cachetools

    ResourceLocation:
        - [本体]
            - src/lib/common_utils/ibr_pickled_table_searcher.py
        - [テストコード]
            - tests/lib/common_utils/ibr_pickled_table_searcher.py

    Todo:
        - パフォーマンスの最適化
        - より複雑な検索条件のサポート
        - データ更新機能の拡張

    Change History:
    | No   | 修正理由           | 修正点                                   | 対応日     | 担当         |
    |------|--------------------|------------------------------------------|------------|--------------|
    | v0.1 | 初期定義作成       | 新規作成                                 | 2024/08/10 |              |
    | v0.2 | キャッシュ機能追加 | キャッシュ処理の実装、更新検知機能の追加 | 2024/08/11 |              |
    """
    def __init__(self, table_name: str, file_path: Path| None = None, df_loader: Callable |None = None,
                get_table_path: Callable | None = None, get_file_modified_time: Callable | None = None,
                load_table: Callable |None = None):
        """TableSearcherクラスのコンストラクタ

        Arguments:
        table_name (str): 検索対象のテーブル名(ファイル名)
        file_path (Path | None): テーブルファイルのパス(オプション)
        df_loader (Callable | None): DataFrameを読み込む関数(オプション)
        get_table_path (Callable | None): テーブルパスを取得する関数(オプション)
        get_file_modified_time (Callable | None): ファイルの更新時刻を取得する関数(オプション)
        load_table (Callable | None): テーブルを読み込む関数(オプション)
        """
        if not table_name or not table_name.strip():
            raise ValueError("テーブル名は空であってはいけません。")

        self.table_name = table_name
        self._get_table_path = get_table_path or self._default_get_table_path
        self.table_path = self._get_table_path()
        self.file_path = file_path or Path(self.table_path) / f"{self.table_name}"
        self._get_file_modified_time = get_file_modified_time or self._default_get_file_modified_time
        self._load_table = load_table or self._default_load_table
        self._df_loader = df_loader or pd.read_pickle
        self.last_modified_time = self._get_file_modified_time()
        self.df, self.is_updated = self._load_table()

    @classmethod
    def create_for_production(cls, table_name: str) -> 'TableSearcher':
        """本番環境用のTableSearcherインスタンスを作成する

        Arguments:
        table_name (str): 検索対象のテーブル名(ファイル名)

        Return Value:
        TableSearcher: 初期化されたTableSearcherインスタンス

        Usage Example:
        >>> searcher = TableSearcher.create_for_production("production_table.pkl")
        """
        return cls(table_name)

    @classmethod
    def create_for_test(cls, table_name: str, mock_file_path: Path, mock_df_loader: Callable,
                        mock_get_table_path: Callable |None = None, mock_get_file_modified_time: Callable |None = None,
                        mock_load_table: Callable | None = None) -> 'TableSearcher':
        """テスト環境用のTableSearcherインスタンスを作成する

        Arguments:
        table_name (str): 検索対象のテーブル名(ファイル名)
        mock_file_path (Path): モックのファイルパス
        mock_df_loader (Callable): モックのDataFrame読み込み関数
        mock_get_table_path (Callable | None): モックのテーブルパス取得関数(オプション)
        mock_get_file_modified_time (Callable | None): モックのファイル更新時刻取得関数(オプション)
        mock_load_table (Callable | None): モックのテーブル読み込み関数(オプション)

        Return Value:
        TableSearcher: 初期化されたTableSearcherインスタンス

        Usage Example:
        >>> mock_path = Path("/mock/path/test_table.pkl")
        >>> mock_loader = lambda _: pd.DataFrame({"col1": [1, 2, 3]})
        >>> searcher = TableSearcher.create_for_test("test_table.pkl", mock_path, mock_loader)
        """
        return cls(table_name, file_path=mock_file_path, df_loader=mock_df_loader,
                    get_table_path=mock_get_table_path,
                    get_file_modified_time=mock_get_file_modified_time,
                    load_table=mock_load_table)

    def _default_get_table_path(self) -> str:
        """デフォルトのテーブルファイルのパスを取得する

        Return Value:
        str: テーブルファイルのパス

        Algorithm:
            1. 現在のディレクトリから、プロジェクトのルートディレクトリを特定
            2. 環境変数またはデフォルト値からパターンを取得
            3. テーブルディレクトリのパスを構築して返す
        """
        current_dir = Path(__file__)
        project_root = current_dir.parent.parent.parent.parent
        exec_pattern = os.environ.get('EXEC_PATTERN', FileConfig.DEFAULT_EXEC_PATTERN)
        return f"{project_root}/{exec_pattern}/{FileConfig.TABLE_DIR_NAME}"

    def _default_get_file_modified_time(self) -> float:
        """ファイルの最終更新時刻を取得する

        Return Value:
        float: ファイルの最終更新時刻(UNIX時間)

        Exceptions:
        FileNotFoundError: ファイルが見つからない場合
        Exception: その他のエラーが発生した場合

        Algorithm:
            1. file_pathの統計情報を取得
            2. 最終更新時刻(st_mtime)を返す
            3. エラーが発生した場合、適切な例外を発生させる
        """
        try:
            return self.file_path.stat().st_mtime
        except FileNotFoundError:
            err_msg = f"ファイル '{self.file_path}' が見つかりません。"
            raise FileNotFoundError(err_msg) from None
        except Exception as e:
            err_msg = f"ファイルの更新時刻の取得中にエラーが発生しました: {str(e)}"
            raise Exception(err_msg) from None

    def _should_update_cache(self) -> bool:
        """キャッシュを更新すべきかどうかを判定する

        Return Value:
        bool: キャッシュを更新すべき場合はTrue、そうでない場合はFalse

        Algorithm:
            1. 現在のファイルの更新時刻を取得
            2. ファイルが存在しない場合、または保存されている最終更新時刻と異なる場合、Trueを返す
            3. そうでない場合はFalseを返す
        """
        try:
            current_modified_time = self.file_path.stat().st_mtime
        except FileNotFoundError:
            return True  # ファイルが存在しない場合はTrue
        else:
            return current_modified_time > self.last_modified_time

    @cached(cache=TTLCache(maxsize=FileConfig.CACHE_MAXSIZE, ttl=FileConfig.CACHE_TTL))
    def _default_load_table(self) -> tuple[pd.DataFrame, bool]:
        """テーブルファイルを読み込む

        Return Value:
        tuple[pd.DataFrame, bool]: 読み込んだDataFrameと更新フラグのタプル

        Exceptions:
        FileNotFoundError: テーブルファイルが見つからない場合
        Exception: その他のエラーが発生した場合

        Algorithm:
            1. キャッシュの更新が必要かチェック
            2. 必要な場合、キャッシュをクリア
            3. ファイルからDataFrameを読み込む、ファイルが存在しない場合はFileNotFoundErrorを返す
            4. 読み込んだDataFrameと更新フラグを返す
        """
        try:
            is_updated = self._should_update_cache()
            if is_updated:
                self._default_load_table.cache_clear()
            _df = self._df_loader(self.file_path)
        except FileNotFoundError:
            err_msg = f"テーブルファイル '{self.table_name}' が見つかりません。"
            raise FileNotFoundError(err_msg) from None
        except Exception as e:
            err_msg = f"テーブルの読み込み中にエラーが発生しました: {str(e)}"
            raise Exception(err_msg) from None
        else:
            return _df, is_updated

    def refresh_data(self) -> None:
        """データを強制的に再読み込みする

        Algorithm:
            1. キャッシュをクリア
            2. テーブルを再読み込み
            3. 内部のDataFrameと更新フラグを更新
        """
        self._default_load_table.cache_clear()
        self.df, self.is_updated = self._default_load_table()

    def simple_search(self, conditions: dict[str, str] | list[dict[str, str]], operator: str = 'AND') -> pd.DataFrame:
        r"""シンプルな条件での検索を行う

        Arguments:
        conditions (dict[str, str] | list[dict[str, str]]): 検索条件
        operator (str): 'AND'または'OR'。デフォルトは'AND'

        Return Value:
        pd.DataFrame: 条件に合致するデータ

        Exceptions:
        ValueError: 無効なoperatorが指定された場合

        Algorithm:
            1. 条件をリスト形式に統一
            2. 各条件セットに対してマスクを作成
            3. operatorに基づいてマスクを組み合わせ
            4. 最終的なマスクを適用してデータを返す

        Notes:
        リファンレスで頻出の上位4桁部店コードでの検索を想定してstartswithのcondtion設定を想定しています

        Usage Example:
        >>> result = searcher.simple_search({"column1": "value1", "column2": "startswith:prefix"}, operator='AND')
        >>> print(result)

        # 1. シンプルな検索 (AND条件)
        and_conditions = {
            "branch_code": f"startswith:{branch_code[:4]}",
            "section_gr_code": f"startswith:{section_gr_code[:4]}",
        }
        print("AND条件での検索結果:")
        and_result = app_searcher.simple_search(and_conditions, operator='AND')
        print(f"該当件数: {len(and_result)}")
        print(and_result.head() if not and_result.empty else "該当するデータがありません。")

        # 2. シンプルな検索 (OR条件)
        or_conditions = {
            "branch_code": f"startswith:{branch_code[:4]}",
            "section_gr_code": f"startswith:{section_gr_code[:4]}",
        }
        print("\nOR条件での検索結果:")
        or_result = app_searcher.simple_search(or_conditions, operator='OR')
        print(f"該当件数: {len(or_result)}")
        print(or_result.head() if not or_result.empty else "該当するデータがありません。")
        """
#        if operator.upper() not in ['AND', 'OR']:
#            err_msg = "operatorは'AND'または'OR'である必要があります。"
#            raise ValueError(err_msg) from None
#
#        if isinstance(conditions, dict):
#            conditions = [conditions]
#
#        masks = []
#        for condition_set in conditions:
#            sub_mask = pd.Series(data=True, index=self.df.index)
#            for column, condition in condition_set.items():
#                if isinstance(condition, str) and condition.startswith('startswith:'):
#                    prefix = condition.split(':', 1)[1]
#                    column_mask = self.df[column].astype(str).str.startswith(prefix)
#                else:
#                    column_mask = self.df[column] == condition
#                sub_mask &= column_mask
#            masks.append(sub_mask)
#
#        if operator.upper() == 'AND':
#            final_mask = pd.concat(masks, axis=1).all(axis=1)
#        else:  # OR
#            final_mask = pd.concat(masks, axis=1).any(axis=1)
#
#
#        print(f"final_mask: \n{final_mask}")
#        result = self.df[final_mask]
#        print(f"simple_search 結果: \n{result}")
#        return result

        if operator.upper() not in ['AND', 'OR']:
            raise ValueError("operatorは'AND'または'OR'である必要があります。")
    
        if isinstance(conditions, dict):
            conditions = [conditions]
    
        masks = []
        for condition_set in conditions:
            sub_masks = []
            for column, condition in condition_set.items():
                if isinstance(condition, str) and condition.startswith('startswith:'):
                    prefix = condition.split(':', 1)[1]
                    column_mask = self.df[column].astype(str).str.startswith(prefix)
                else:
                    column_mask = self.df[column].astype(str) == str(condition)
                sub_masks.append(column_mask)
            
            if operator.upper() == 'AND':
                sub_mask = pd.concat(sub_masks, axis=1).all(axis=1)
            else:  # OR
                sub_mask = pd.concat(sub_masks, axis=1).any(axis=1)
            
            masks.append(sub_mask)
    
        final_mask = pd.concat(masks, axis=1).any(axis=1)
        
        return self.df[final_mask]



    def advanced_search(self, condition_func: Callable[[pd.DataFrame], pd.Series]) -> pd.DataFrame:
        r"""高度な条件での検索を行う

        Arguments:
        condition_func (Callable[[pd.DataFrame], pd.Series]): DataFrameを引数に取り、ブールのSeriesを返す関数

        Return Value:
        pd.DataFrame: 条件に合致するデータ

        Algorithm:
            1. 引数として与えられた関数にDataFrameを渡して条件を評価
            2. 評価結果のブールマスクを使用してデータをフィルタリング

        Usage Example:
        >>> def condition(df):
        ...     return (df['column1'] > 10) & (df['column2'].str.startswith('A'))
        >>> result = searcher.advanced_search(condition)
        >>> print(result)

        # 3. 高度な検索
        def advanced_condition(df):
            return (
                df['branch_code'].astype(str).str.startswith(branch_code[:4]) &
                df['section_gr_code'].astype(str).str.startswith(section_gr_code[:4])
            )

        print("\n高度な条件での検索結果:")
        advanced_result = app_searcher.advanced_search(advanced_condition)
        print(f"該当件数: {len(advanced_result)}")
        print(advanced_result.head() if not advanced_result.empty else "該当するデータがありません。")
        """
        try:
            result = condition_func(self.df)
            if not isinstance(result, pd.Series):
                raise ValueError("条件関数の結果がpd.Series型ではありません")
            if result.dtype != bool:
                raise ValueError("条件関数の結果がブール型のSeriesではありません")
            return self.df[result]
        except Exception as e:
            raise Exception(f"Invalid condition function result: {str(e)}") from e
