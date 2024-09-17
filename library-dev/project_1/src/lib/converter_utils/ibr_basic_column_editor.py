from typing import Any

class ColumnEditor:
    """カラム編集の基底クラス

    Class Overview:
        このクラスは、データフレームの特定のカラムに対する編集操作を定義するための基底クラスです。
        サブクラスは _edit_value メソッドをオーバーライドして具体的な編集ロジックを実装します。

    Attributes:
        なし

    Condition Information:
        - Condition:1
            - ID: VALUE_TYPE_CHECK
            - Type: Type Checking
            - Applicable Scenarios: 入力値の型チェック

    Pattern Information:
        - Pattern:1
            - ID: TEMPLATE_METHOD
            - Type: Design Pattern
            - Applicable Scenarios: 共通のインターフェースを持つ異なる編集操作の実装

    Methods:
        edit(value: Any): 値を編集する
        _edit_value(value: int | float): 具体的な編集操作を行う(サブクラスでオーバーライド)
    Usage Example:
        >>> editor = ColumnEditor()
        >>> result = editor.edit(5)
        >>> print(result)
        5

    Notes:
        - このクラスは直接インスタンス化せず、サブクラスを通じて使用することを想定しています。
        - サブクラスは必ず _edit_value メソッドをオーバーライドする必要があります。

    Dependency:
        - typing

    ResourceLocation:
        - [本体]
            - /path/to/column_editors.py
        - [テストコード]
            - /path/to/test_column_editors.py

    Todo:
        - エラー処理の強化
        - より多様な型に対応するための拡張

    Change History:
    | No   | 修正理由     | 修正点   | 対応日     | 担当         |
    |------|--------------|----------|------------|--------------|
    | v0.1 | 初期定義作成 | 新規作成 | 2024/09/07 |              |

    """

    def edit(self, value: Any) -> Any:
        """値を編集する

        Arguments:
        value (Any): 編集対象の値

        Return Value:
        Any: 編集後の値

        Algorithm:
            1. 入力値が数値型(int または float)かどうかをチェック
            2. 数値型の場合、_edit_value メソッドを呼び出して編集
            3. 数値型でない場合、値をそのまま返す

        Exception:
        なし

        Usage Example:
        >>> editor = ColumnEditor()
        >>> result = editor.edit(5)
        >>> print(result)
        5
        """
        if isinstance(value, int | float):
            return self._edit_value(value)
        return value

    def _edit_value(self, value: int | float) -> int | float:
        """具体的な編集操作を行う(サブクラスでオーバーライド)

        Arguments:
        value (int | float): 編集対象の数値

        Return Value:
        int | float: 編集後の数値

        Exceptions:
        NotImplementedError: このメソッドが直接呼び出された場合

        Algorithm:
            サブクラスで実装

        Usage Example:
        >>> # このメソッドは直接呼び出さず、サブクラスでオーバーライドして使用します

        Notes:
        - このメソッドは抽象メソッドとして機能し、サブクラスでの実装を強制します
        """
        err_msg = "Subclasses must implement the '_edit_value' method."
        raise NotImplementedError(err_msg) from None


class Column1Editor(ColumnEditor):
    def _edit_value(self, value: int | float) -> int | float:
        return 10 if value == 1 else value

class Column2Editor(ColumnEditor):
    def _edit_value(self, value: int | float) -> int | float:
        return -1 if value == 0 else value

class Column3Editor(ColumnEditor):
    def _edit_value(self, value: int | float) -> int | float:
        return value * 2

class Column4Editor(ColumnEditor):
    def edit(self, value: int | float) -> int | float:
        return 100 if value == 0 else value

class Column5Editor(ColumnEditor):
    def _edit_value(self, value: int | float) -> int | float:
        return 0 if value >= 2 else value

class Column6Editor(ColumnEditor):
    def edit(self, value: int | float) -> int | float:
        return 10 if value >= 3 else value

class Column7Editor(ColumnEditor):
    def _edit_value(self, value: int | float) -> int | float:
        return str(value) + "_"

class Column8Editor(ColumnEditor):
    def _edit_value(self, value: int | float) -> int | float:
        return str(value) + "*"
