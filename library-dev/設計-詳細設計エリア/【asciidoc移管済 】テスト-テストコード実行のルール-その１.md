# テスト環境設定

## テストコード実行の際のルール
### terminalセッションで環境設定変数を定義する
- 環境変数名: EXEC_PATTERN=tests
  - ubuntu
    - export EXEC_PATTERN=tests
  - windows
    - $ENV:EXEC_PATTERN='tests'

環境設定変数によりtests系ディレクトリのlogにテストログが出力されるようになります。

### pytest実行
- `project` 直下に移動
  - pytest -lvs ./tests/lib/converter_utils/test_ibr_excel_field_analyzer.py 
  - 状況によっては 
    - pytest -lv ./tests/lib/converter_utils/test_ibr_excel_field_analyzer.py 

---

## debuger vsc設定
デバッグにより検証する場合は以下の設定を行ってください。

原則プロジェクト全体での設定ではなく各個人でカスタムして利用してください。

### デバッグ構成を作成する
- VS Code の左サイドバーにある「デバッグ」アイコンをクリック
- デバッグビューの「構成の追加」をクリック
- 「Python: モジュールの実行」を選択
- `launch.json`ファイルが作成され、以下のような構成が追加されます。
```
{
  "name": "Python: モジュールの実行",
  "type": "python",
  "request": "launch",
  "module": "your_package_name",
  "console": "integratedTerminal",
  "justMyCode": true
}
```
### テスト対象コードに対してDebugger設定／Debug実行

- `module`
  - テスト対象モジュールパスを.形式で指定する
    - case1 -m 形式で__main__.pyを起動する形式の場合はモジュールパッケージパスまで設定
    - case2 直接起動する場合はモジュールパス(ただし.pyは書かない)を設定

- `cwd`
  - プロジェクトパスを指定すること

```
## module/file起動バターン
// launch.json sample
            "name": "Python: Module",
            "type": "python",
            "request": "launch",
            // テスト対象モジュールパスを.形式で指定する
            // case1 -m 形式で__main__.pyを起動する形式の場合はモジュールパッケージパスまで設定
            // case2 直接起動する場合はモジュールパス(ただし.pyは書かない)を設定
            //"module": "src.package.validator_excel_main_class-2",            // case1
            "module": "src.lib.validator_utils.ibr_check_reference_exists",  // case2
            // プロジェクトパスを指定すること
            "cwd": "${workspaceFolder}/library-dev/project_1/",
            "console": "integratedTerminal",
```

- テスト対象モジュールで`break point`を設定して`Debugger`実行してください
  - 以後はProject固有の設定はありません
  - 詳細はVSCのガイドを参照してください

---
```
## pytest起動パターン
// launch.json sample
            "name": "Python: pytest",
            "type": "python",
            "request": "launch",
            "module": "pytest",
            "args": [
                "-lvs",                                                         // pytest引数
                "tests/lib/validator_utils/test_ibr_check_reference_exists.py"  //テスト関数を指定、.pyも付与する
            ],
            "cwd": "${workspaceFolder}/library-dev/project_1/",
            "console": "integratedTerminal"
```