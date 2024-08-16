# check_commands.py

import pandas as pd
from typing import List
import toml

class ValidationCheckCommand(CheckCommand):
    def execute(self, df: pd.DataFrame) -> pd.DataFrame:
        # 既存のバリデーションロジックをここに実装
        # エラーがあれば、dfにエラー列を追加
        return df

class ConsistencyCheckCommand(CheckCommand):
    def execute(self, df: pd.DataFrame) -> pd.DataFrame:
        # 既存の整合性チェックロジックをここに実装
        # エラーがあれば、dfにエラー列を追加
        return df

class BlacklistCheckCommand(CheckCommand):
    def __init__(self, blacklist_file: str):
        with open(blacklist_file, "r") as f:
            self.blacklist = toml.load(f)["blacklist"]

    def execute(self, df: pd.DataFrame) -> pd.DataFrame:
        df['blacklist_alert'] = df.apply(self._check_blacklist, axis=1)
        return df

    def _check_blacklist(self, row):
        for entry in self.blacklist:
            if entry["部店コード"] == row["部店コード"] and entry["課Grコード"] == row["課Grコード"]:
                for 業務 in entry["業務種別"]:
                    if 業務["業務名"] == row["業務名"]:
                        return f"アラート: {業務['アラートメッセージ']} 対応手順: {業務['対応手順']}"
        return ""

class CheckCommandInvoker:
    def __init__(self, commands: List[CheckCommand]):
        self.commands = commands

    def execute_all(self, df: pd.DataFrame) -> pd.DataFrame:
        for command in self.commands:
            df = command.execute(df)
        return df
