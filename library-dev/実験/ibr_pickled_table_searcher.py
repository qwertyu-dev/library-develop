import pandas as pd
from pathlib import Path
import os

class Config:
    DEFAULT_EXEC_PATTERN = 'src'
    TABLE_DIR_NAME = 'table'

class TableSearcher:
    def __init__(self, table_name):
        self.table_name = table_name
        self.table_path = self._get_table_path()
        self.df = self._load_table()

    def _get_table_path(self):
        current_dir = Path.cwd()
        project_root = current_dir.parent.parent.parent
        exec_pattern = os.environ.get('EXEC_PATTERN', Config.DEFAULT_EXEC_PATTERN)
        return f"{project_root}/{exec_pattern}/{Config.TABLE_DIR_NAME}"

    def _load_table(self):
        file_path = Path(self.table_path) / f"{self.table_name}"
        try:
            return pd.read_pickle(file_path)
        except FileNotFoundError:
            raise FileNotFoundError(f"テーブルファイル '{self.table_name}' が見つかりません。")
        except Exception as e:
            raise Exception(f"テーブルの読み込み中にエラーが発生しました: {str(e)}")

    def search(self, conditions):
        mask = pd.Series(True, index=self.df.index)
        for column, condition in conditions.items():
            if isinstance(condition, str) and condition.startswith('startswith:'):
                prefix = condition.split(':', 1)[1]
                column_mask = self.df[column].astype(str).str.startswith(prefix)
            else:
                column_mask = self.df[column] == condition
            mask &= column_mask
        return self.df[mask]

    def get_all(self):
        return self.df

    def get_column_info(self, column_name):
        if column_name not in self.df.columns:
            return f"カラム '{column_name}' は存在しません。"
        
        column_data = self.df[column_name]
        return f"""
        カラム '{column_name}' の情報:
        データ型: {column_data.dtype}
        ユニークな値の数: {column_data.nunique()}
        最初の5つのユニークな値: {column_data.unique()[:5]}
        null値の数: {column_data.isnull().sum()}
        """

# 使用例
if __name__ == "__main__":
    try:
        app_searcher = TableSearcher("df_integrated_layout.pkl")
        
        # データに存在する値を使用（実際の値に応じて調整してください）
        branch_code = "94451"
        section_gr_code = "12771"
        
        conditions = {
            "branch_code": f"startswith:{branch_code[:4]}",
            "section_gr_code": f"startswith:{section_gr_code[:4]}",
        }
        print(f"検索条件: {conditions}")
        
        print("\nカラム情報:")
        print(app_searcher.get_column_info("branch_code"))
        print(app_searcher.get_column_info("section_gr_code"))
        
        result = app_searcher.search(conditions)
        
        print("\n検索結果:")
        if result.empty:
            print("該当するデータがありません。")
        else:
            print(f"該当件数: {len(result)}")
            print(result.head())  # 最初の5行を表示

        print("\n全データの概要:")
        all_data = app_searcher.get_all()
        print(f"総行数: {len(all_data)}")
        print("最初の5行:")
        print(all_data.head())

    except Exception as e:
        print(f"エラーが発生しました: {str(e)}")
