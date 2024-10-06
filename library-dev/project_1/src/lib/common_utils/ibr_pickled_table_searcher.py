from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path
from typing import TypeAlias

import pandas as pd
from cachetools import TTLCache, cached

from src.lib.common_utils.ibr_enums import LogLevel
from src.lib.common_utils.ibr_decorator_config import with_config

# typeエイリアス定義
ConditionDict: TypeAlias = dict[str, str]
ConditionList: TypeAlias = list[ConditionDict]

@dataclass(frozen=True)
class FileConfig:
    """デフォルト値定数定義"""
    CACHE_MAXSIZE: int = 100
    CACHE_TTL: int = 3600

class ErrorMessages:
    EMPTY_TABLE_NAME = "pickleテーブル名は空であってはいけません : {table_name}"
    FILE_NOT_FOUND = "ファイル '{file_path}' が見つかりません。"
    FILE_UPDATE_TIME_ERROR = "ファイルの更新時刻の取得中にエラーが発生しました: {error}"
    TABLE_LOAD_ERROR = "テーブルの読み込み中にエラーが発生しました: {error}"
    INVALID_OPERATOR = "operatorは'AND'または'OR'である必要があります: {operator}"
    INVALID_CONDITION_FUNC_RESULT = "条件関数の結果が{expected_type}型ではありません: {actual_result}"
    INVALID_CONDITION_FUNCTION = "無効な条件関数の結果: {error}"

class PickledTableSearchError(Exception):
    pass

def raise_type_err(msg: str) -> None:
    # Ruff
    raise TypeError(msg) from None

@with_config
class TableSearcher:
    """テーブルデータの検索と情報取得を行うクラス

    Class Overview:
        このクラスは、pickleファイルとして保存されたテーブルデータを読み込み、
        様々な条件での検索機能を提供します。シンプルな検索と高度な検索の両方をサポートし、
        データのキャッシュ管理も行います。

    Attributes:
        env (str): 実行環境
        common_config (dict): 共通設定
        package_config (dict): パッケージ固有の設定
        log_msg (callable): ログメッセージ出力関数
        table_name (str): 検索対象のテーブル名
        file_path (Path): pickleファイルのパス
        get_file_modified_time (Callable[[], float]): ファイルの最終更新時刻を取得する関数
        df (pd.DataFrame): 読み込まれたテーブルデータ
        last_modified_time (float): 最後にファイルを読み込んだ時刻

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
        - cachetools
        - pathlib

    ResourceLocation:
        - [本体]
            - src/lib/common_utils/ibr_pickled_table_searcher.py
        - [テストコード]
            - tests/lib/common_utils/test_ibr_pickled_table_searcher.py

    Todo:
        - パフォーマンスの最適化
        - より複雑な検索条件のサポート
        - データ更新機能の拡張

    Change History:
    | No   | 修正理由           | 修正点                                   | 対応日     | 担当         |
    |------|--------------------|------------------------------------------|------------|--------------|
    | v0.1 | 初期定義作成       | 新規作成                                 | 2024/07/20 | xxxx aaa.bbb |
    | v0.2 | キャッシュ機能追加 | キャッシュ処理の実装、更新検知機能の追加 | 2024/07/25 | yyyy ccc.ddd |
    """

    def __init__(
        self,
        table_name: str,
        file_path: Path | None = None,
        get_file_modified_time: Callable[[], float] | None = None,
        config: dict | None = None,
    ):
        """イニシャライザ

        Arguments:
        table_name (str): 検索対象のテーブル名
        file_path (Path | None): pickleファイルのパス。Noneの場合はデフォルトパスが使用される
        get_file_modified_time (Callable[[], float] | None): ファイルの最終更新時刻を取得する関数。Noneの場合はデフォルト関数が使用される
        config: configのDI 
        """
        # configのDI
        self.config = config or self.config
        self.env = self.config.env
        self.common_config = self.config.common_config
        self.package_config = self.config.package_config
        self.log_msg = self.config.log_message

        self.log_msg(f"TableSearcher.__init__ called. self.config: {getattr(self, 'config', 'Not set')}", LogLevel.INFO)

        # table_name
        self.log_msg(f'table_name: {table_name}', LogLevel.INFO)
        if not table_name or not table_name.strip():
            msg = f"{ErrorMessages.EMPTY_TABLE_NAME}"
            raise ValueError(msg) from None
        self.table_name = table_name

        # file_path
        self.log_msg(f'file_path: {file_path}', LogLevel.INFO)
        if file_path:
            self.file_path = Path(file_path) / self.table_name
        else:
            self.file_path = Path(self.common_config.get('optional_path', []).get('TABLE_PATH', '')) / self.table_name
        self.log_msg(f'self.file_path: {self.file_path}', LogLevel.INFO)

        self.get_file_modified_time = get_file_modified_time or self._default_get_file_modified_time
        self.df = self._default_load_table()
        self.last_modified_time = self.get_file_modified_time()

    def _default_get_file_modified_time(self) -> float:
        """ファイルの最終更新時刻を取得する"""
        try:
            self.log_msg(f'pickle_file_path: {self.file_path}', LogLevel.INFO)
            return self.file_path.stat().st_mtime
        except FileNotFoundError:
            err_msg = f"{ErrorMessages.FILE_NOT_FOUND}"
            raise FileNotFoundError(err_msg) from None
        except Exception as e:
            err_msg = f"{ErrorMessages.FILE_UPDATE_TIME_ERROR}"
            raise Exception(err_msg) from e

    def _should_update_cache(self) -> bool:
        """キャッシュを更新すべきかどうかを判定する"""
        try:
            current_modified_time = self.get_file_modified_time()
        except FileNotFoundError:
            return True
        else:
            return current_modified_time > self.last_modified_time

    @cached(cache=TTLCache(maxsize=FileConfig.CACHE_MAXSIZE, ttl=FileConfig.CACHE_TTL))
    def _default_load_table(self) -> pd.DataFrame:
        """テーブルファイルを読み込む"""
        try:
            if self._should_update_cache():
                self._default_load_table.cache_clear()
            return pd.read_pickle(self.file_path)
        except FileNotFoundError as e:
            err_msg = f"{ErrorMessages.FILE_NOT_FOUND}"
            raise FileNotFoundError(err_msg) from e
        except Exception as e:
            err_msg = f"{ErrorMessages.TABLE_LOAD_ERROR}"
            raise Exception(err_msg) from e

    def simple_search(self, conditions: ConditionDict | ConditionList, operator: str = 'AND') -> pd.DataFrame:
        """シンプルな条件での検索を行う

        このメソッドは、指定された条件に基づいてデータフレームをフィルタリングします。
        等値検索と前方一致検索(startswith)をサポートしています。

        Arguments:
        conditions (ConditionDict | ConditionList): 検索条件。以下の形式をサポート:
            - 単一条件: {"column_name": "value"}
            - 複数条件: {"column1": "value1", "column2": "value2"}
            - 前方一致: {"column_name": "startswith:prefix"}
            - 複数条件のリスト: [{"column1": "value1"}, {"column2": "value2"}]
        operator (str): 'AND'または'OR'。デフォルトは'AND'
            - 'AND': 全ての条件を満たすデータを返す
            - 'OR': いずれかの条件を満たすデータを返す

        Return Value:
        pd.DataFrame: 条件に合致するデータ

        Algorithm:
            1. 検索条件を正規化する
            2. 条件に基づいてマスクを作成する
                - 通常の条件: 完全一致
                - 'startswith:' プレフィックス付きの条件: 前方一致
            3. operator(AND/OR)に基づいてマスクを結合する
            4. 最終的なマスクを適用してデータをフィルタリングする

        Exceptions:
        ValueError: 無効なoperatorが指定された場合

        Usage Example:
        # 1. 単一の等値検索
        >>> result = searcher.simple_search({"column1": "value1"})

        # 2. 複数条件のAND検索
        >>> result = searcher.simple_search({"column1": "value1", "column2": "value2"}, operator='AND')

        # 3. 前方一致検索
        >>> result = searcher.simple_search({"column_name": "startswith:prefix"})

        # 4. 複数条件のOR検索(等値と前方一致の組み合わせ)
        >>> result = searcher.simple_search([
        ...     {"column1": "value1"},
        ...     {"column2": "startswith:pre"}
        ... ], operator='OR')

        Notes:
        - 'startswith:' プレフィックスを使用することで、指定したカラムの値が特定のプレフィックスで始まるデータを検索できます。
        - 大文字小文字は区別されます。必要に応じて、条件値を適切に調整してください。
        - パフォーマンスに関する注意: 大規模なデータセットに対して複雑な条件や多数の'OR'条件を使用する場合、検索に時間がかかる可能性があります。そのような場合は、advanced_search メソッドの使用を検討してください。
        """
        if operator.upper() not in ['AND', 'OR']:
            err_msg = f"{ErrorMessages.INVALID_OPERATOR}"
            raise ValueError(err_msg)

        normalized_conditions = self._normalize_conditions(conditions)
        masks = self._create_masks(normalized_conditions, operator)
        final_mask = pd.concat(masks, axis=1).any(axis=1)
        return self.df[final_mask]

    def _normalize_conditions(self, conditions: ConditionDict | ConditionList) -> ConditionList:
        """検索条件を正規化する"""
        return [conditions] if isinstance(conditions, dict) else conditions

    def _create_masks(self, conditions: ConditionList, operator: str) -> list[pd.Series]:
        """条件に基づいてマスクを作成する"""
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
        return masks

    def advanced_search(self, condition_func: Callable[[pd.DataFrame], pd.Series]) -> pd.DataFrame:
        """高度な条件での検索を行う

        Arguments:
        condition_func (Callable[[pd.DataFrame], pd.Series]): DataFrameを引数に取り、ブールのSeriesを返す関数

        Return Value:
        pd.DataFrame: 条件に合致するデータ

        Algorithm:
            1. 引数として与えられた関数にDataFrameを渡して条件を評価
            2. 評価結果のブールマスクを使用してデータをフィルタリング

        Exceptions:
        PickledTableSearchError: 無効な条件関数が指定された場合

        Usage Example:
        >>> def condition(df):
        ...     return (df['column1'] > 10) & (df['column2'].str.startswith('A'))
        >>> searcher = TableSearcher("example_table.pkl")
        >>> result = searcher.advanced_search(condition)
        >>> print(result)
        """
        try:
            result = condition_func(self.df)
            if not isinstance(result, pd.Series):
                raise_type_err(f"{ErrorMessages.INVALID_CONDITION_FUNC_RESULT}")
            if result.dtype != bool:
                raise_type_err(f"{ErrorMessages.INVALID_CONDITION_FUNC_RESULT}")
        except Exception as e:
            err_msg = f"{ErrorMessages.INVALID_CONDITION_FUNCTION}"
            raise PickledTableSearchError(err_msg) from e
        return self.df[result]
