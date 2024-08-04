"""
コードの説明:

validators.py:
検証関数 validate_age と validate_marriage を定義しています。
これらの関数は、フィールド値の検証ロジックを含みます。

models.py:
Person モデルを定義しています。
age フィールドに validate_age 関数を、@model_validator デコレータに validate_marriage 関数を適用しています。


main.py:
Excelファイルからデータを読み込み、df DataFrameに格納します。
validate_row 関数を定義し、Person モデルを使用して各行の検証を行います。

検証が成功した場合は、モデルのディクショナリを返します。
検証が失敗した場合は、元の行のデータとエラーメッセージを含むディクショナリを返します。

df.apply メソッドを使用して、各行に validate_row 関数を適用し、validated_data を取得します。
validated_data.tolist() を使用してリストに変換し、pd.DataFrame を使用して新しいDataFrame validated_df を作成します。
最後に、validated_df を出力します。

この構成により、検証ロジックとモデルが別のモジュールに分離され、メインのコードがすっきりとしています。また、apply メソッドを使用して効率的に検証を行い、エラー発生時のデータ出力も組み込まれています。

# sample

Validated DataFrame:
    name  age  is_married                                              error
0   John   25        True                                                NaN
1  Alice   -5       False             Age must be non-negative             
2    Bob   17        True  Person must be at least 18 years old to be ma...
3   Mike   30       False                                                NaN

"""


# validators.py

from pydantic import ValidationError

def validate_age(value):
    if value < 0:
        raise ValueError('Age must be non-negative')
    return value

def validate_marriage(values):
    age = values.get('age')
    is_married = values.get('is_married')
    if is_married and age < 18:
        raise ValueError('Person must be at least 18 years old to be married')


# models.py

from pydantic import BaseModel, Field, model_validator
from validators import validate_age, validate_marriage

class Person(BaseModel):
    name: str
    age: int = Field(..., validator=validate_age)
    is_married: bool

    @model_validator
    def validate(cls, values):
        validate_marriage(values)


# main.py

import pandas as pd
from models import Person
from validators import ValidationError

# Excelファイルからデータを読み込む
df = pd.read_excel('data.xlsx')

# 検証関数の定義
def validate_row(row):
    try:
        person = Person(**row.to_dict())
        return person.dict()
    except ValidationError as e:
        error_dict = row.to_dict()
        error_dict["error"] = str(e)
        return error_dict

# DataFrameの各行に検証を適用
validated_data = df.apply(validate_row, axis=1)

# 検証済みのデータを新しいDataFrameに変換
validated_df = pd.DataFrame(validated_data.tolist())

# 結果の出力
print("Validated DataFrame:")
print(validated_df)
