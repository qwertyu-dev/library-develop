# poetry_test

## pyenvでlocalのPythonバージョンを指定する
- pyenv install で必要となる複数のpythonを導入する
```
pyenv install --list
pyenv install 3.11.6
pyenv install 3.11.x
```

## 出てこないバージョンのpyenvでのpythonインストール
### https://blog.aoirint.com/entry/2023/python_init_project/#pythonpoetry%E3%81%AE%E3%82%A4%E3%83%B3%E3%82%B9%E3%83%88%E3%83%BC%E3%83%AB
```
env PYTHON_CONFIGURE_OPTS="--enable-shared" pyenv install 3.11.6
```
## Poetryのグローバル設定を変更し、Python仮想環境がプロジェクトのディレクトリ/.venvに作成されるようにします
```
poetry config virtualenvs.in-project true
```


## 使用するpythonバージョンを指定する
globalはシステム全体で使うバージョンを変えたいときに使用。localはプロジェクトごとで違うバージョンを使いたいときに使用。
```
mkdir sandbox1; cd $_

# なければ作る↓
cat .python-version
3.11.6

pyenv local or pyenv globalを実行する
```

```
pyenv local; python -V
3.11.6
Python 3.11.6
```
---
## poetryでpython指定環境を使用できるようにする
```
ENV_PYTHON=$(pyenv which python)
poetry env use ${ENV_PYTHON}
```

## poetry初期設定(全くの初期から)
### 対話式で導入
- pythonのバージョンはpyenvで設定したものを示すこと
- git cloneからpoetry init済の資源を取れる状態であるならば改めての実行は不要
```
poetry init
```
### 通常はgitに登録済のはず
git cloneで仕込み済資源を持ってくるだけでもOK

---
## パッケージインストール
### まとめてパッケージをインストール
`pyproject.toml`に定義を書きます
```
[tool.poetry.dependencies]
python = "3.11.6"
requests = "^2.31.0"
numpy = "^1.26.2"
pandas = "^2.1.4"
pydantic = "^2.5.2"
```
その後はいつもどおり
```
poetry install
```

### うまくいかない時
```
poetry env use 3.11.6
```

---

### 追加でパッケージを追加する
```
poetry add requests

The currently activated Python version 3.8.11 is not supported by the project (3.11.6).
Trying to find and use a compatible version. 
Using python3 (3.11.6)
Using version ^2.31.0 for requests

Updating dependencies
Resolving dependencies... (0.1s)

Writing lock file

Package operations: 5 installs, 0 updates, 0 removals

  • Installing certifi (2023.11.17)
  • Installing charset-normalizer (3.3.2)
  • Installing idna (3.6)
  • Installing urllib3 (2.1.0)
  • Installing requests (2.31.0)
```

## 追加パッケージの確認
いくつか方法があります

### インストール済みの依存パッケージの一覧を表示
これでrequestsがリストに含まれていることを確認
```
$ poetry show -t
The currently activated Python version 3.8.11 is not supported by the project (3.11.6).
Trying to find and use a compatible version. 
Using python3 (3.11.6)
requests 2.31.0 Python HTTP for Humans.
├── certifi >=2017.4.17
├── charset-normalizer >=2,<4
├── idna >=2.5,<4
└── urllib3 >=1.21.1,<3
```

### Pythonのpipが見ているインストール済みパッケージを確認
pip listのリストにrequestsが存在すればOK
```
$ poetry run pip list
The currently activated Python version 3.8.11 is not supported by the project (3.11.6).
Trying to find and use a compatible version. 
Using python3 (3.11.6)
Package            Version
------------------ ----------
certifi            2023.11.17
charset-normalizer 3.3.2
idna               3.6
pip                22.2.2
requests           2.31.0
setuptools         65.3.0
urllib3            2.1.0
wheel              0.37.1

[notice] A new release of pip available: 22.2.2 -> 23.3.1
[notice] To update, run: pip install --upgrade pip
```
### 仮想環境に入りPythonインタプリタからimportしエラーが出なければ導入済みを意味します
```
$ poetry shell
The currently activated Python version 3.8.11 is not supported by the project (3.11.6).
Trying to find and use a compatible version. 
Using python3 (3.11.6)
Spawning shell within /home/satoshi/.cache/pypoetry/virtualenvs/poetry-test-82y1yN3c-py3.11
. /home/satoshi/.cache/pypoetry/virtualenvs/poetry-test-82y1yN3c-py3.11/bin/activate
satoshi@server:/developer/poetry_sandbox/test_package1/poetry_test$ . /home/satoshi/.cache/pypoetry/virtualenvs/poetry-test-82y1yN3c-py3.11/bin/activate
(poetry-test-py3.11) satoshi@server:/developer/poetry_sandbox/test_package1/poetry_test$ python -c 'import requests'
(poetry-test-py3.11) satoshi@server:/developer/poetry_sandbox/test_package1/poetry_test$ 
```

### pyproject.tomlファイルを確認し、dependenciesセクションにrequestsが追加されているかどうかを確認
```
$ cat pyproject.toml 
[tool.poetry]
name = "poetry-test"
version = "0.1.0"
description = ""
authors = ["satoshi <satoshi@kawagucchi.net>"]
readme = "README.md"
packages = [{include = "poetry_test"}]

[tool.poetry.dependencies]
python = "3.11.6"
requests = "^2.31.0"


[build-system]
requires = ["poetry-core"]
build-backend = "poetry.core.masonry.api"
```

