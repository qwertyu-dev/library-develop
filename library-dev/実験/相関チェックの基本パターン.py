# 必要なライブラリをインストールするには以下のコマンドを使用してください。
# pip install pandas pydantic

import pandas as pd
from pydantic import BaseModel, ValidationError, root_validator, conint

# サンプルのデータを作成
data = {
    'name': ['Alice', 'Bob', 'Charlie'],
    'age': [25, 17, 35],
    'email': ['alice@example.com', 'bob@example.com', 'charlie@invalid']
}

df = pd.DataFrame(data)

# Pydanticモデルを定義し、カスタムバリデーションを追加
class Person(BaseModel):
    name: str
    age: conint(ge=0)  # age must be a non-negative integer
    email: str

    @root_validator
    def check_email_if_adult(cls, values):
        age = values.get('age')
        email = values.get('email')
        if age is not None and age >= 18:
            # ageが18歳以上の場合、emailが有効である必要がある
            if email is None or '@' not in email:
                raise ValueError('Adults must have a valid email address')
        return values

# DataFrameの各行をバリデートする関数
def validate_dataframe(df):
    for index, row in df.iterrows():
        try:
            person = Person(**row.to_dict())
            print(f"Row {index} is valid: {person}")
        except ValidationError as e:
            print(f"Row {index} is invalid: {e}")

# DataFrameのバリデーションを実行
validate_dataframe(df)
