## Response:
はい、モデルに定義するレイアウトとバリデーションのサンプルを提示します。ここでは、人事、国企、関連の3つのモデルについて、それぞれ一部の属性とバリデーションルールを示します。

```python
# excel_jinji_model.py
from pydantic import BaseModel, Field, validator

class ExcelJinjiModel(BaseModel):
    employee_id: str = Field(min_length=5, max_length=10)
    name: str = Field(min_length=1, max_length=100)
    department: str = Field(min_length=1, max_length=50)
    salary: int = Field(gt=0)

    @validator('employee_id')
    def employee_id_must_start_with_j(cls, v):
        if not v.startswith('J'):
            raise ValueError('employee_id must start with "J"')
        return v
```

この例では、人事モデルに4つの属性を定義しています：

* `employee_id`: 5～10文字の文字列で、"J"で始まる必要があります。
* `name`: 1～100文字の文字列です。
* `department`: 1～50文字の文字列です。
* `salary`: 0より大きい整数です。

`employee_id` には、カスタムバリデーターを定義し、値が "J" で始まることを確認しています。

```python
# excel_kokki_model.py
from pydantic import BaseModel, Field, validator
from datetime import date

class ExcelKokkiModel(BaseModel):
    project_id: str = Field(min_length=5, max_length=10)
    project_name: str = Field(min_length=1, max_length=100)
    start_date: date
    end_date: date

    @validator('end_date')
    def end_date_must_be_after_start_date(cls, v, values):
        if 'start_date' in values and v < values['start_date']:
            raise ValueError('end_date must be after start_date')
        return v
```

この例では、国企モデルに4つの属性を定義しています：

* `project_id`: 5～10文字の文字列です。
* `project_name`: 1～100文字の文字列です。
* `start_date`: 日付型です。
* `end_date`: 日付型で、`start_date` より後の日付である必要があります。

`end_date` には、カスタムバリデーターを定義し、`start_date` より後の日付であることを確認しています。

```python
# excel_kanren_model.py
from pydantic import BaseModel, Field, EmailStr

class ExcelKanrenModel(BaseModel):
    supplier_id: str = Field(min_length=5, max_length=10)
    supplier_name: str = Field(min_length=1, max_length=100)
    contact_name: str = Field(min_length=1, max_length=100)
    email: EmailStr
```

この例では、関連モデルに4つの属性を定義しています：

* `supplier_id`: 5～10文字の文字列です。
* `supplier_name`: 1～100文字の文字列です。
* `contact_name`: 1～100文字の文字列です。
* `email`: 有効なメールアドレス形式である必要があります。

`email` には、Pydanticの `EmailStr` 型を使用し、有効なメールアドレス形式であることを確認しています。

これらは単なる例ですが、実際のモデルでは、各レイアウトに応じた属性とバリデーションルールを定義します。Pydanticは、型ヒントとデコレーターを使用して、多様なバリデーションルールを簡潔に表現できます。

何か質問やご要望があれば、お気軽にお知らせください。

