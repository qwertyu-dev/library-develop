"""Excel一括申請シートのCell分析Utilty

一括申請によるExcelに対する個別の部品を定義する

"""
import re
import sys
import unicodedata

from src.lib.common_utils.ibr_decorator_config import initialize_config
from src.lib.common_utils.ibr_enums import LogLevel

config = initialize_config(sys.modules[__name__])
log_msg = config.log_message

class RemarksParser:
    """備考欄の文字列を解析し、営業部署、エリアグループ、その他の情報を抽出するクラス。

    業務要件:
    - 備考欄の形式:
        - 各項目は異なる行に記載される。
        - 項目の例:
            - 営業部傘下の課の所属営業部
            - 部店・課Grの復活
            - 名称変更, 部門変更・エリアコード変更
            - エリア情報ファイルの共通認証受渡し初日
            - エリア課Gr情報
    - 営業部傘下の課の所属営業部:
        - 「○○支店営業部」,「○○支店営業第○部」もしくは「○○営業部営業部」,「○○営業部営業第○部」の形式で記載される。
    - エリア課Gr情報:
        - 英数字5桁 + 全角または半角スペース + Grを含む文字列 + (設立日) の形式で記載される。
    - 「変更」「廃止」「共通認証」を含む行は読み飛ばし、その他の情報として扱う。

    - 出力様式
        - parseメソッド仕様を参照
    """
    def __init__(self):
        self.result: dict[str, dict[str, str]] = {
            "request_type": "",
            "sales_department": {
                "department_name": "",
                "branch_name": "",
            },
            "area_group": {
                "group_code": "",
                "group_name": "",
                "established_date": "",
            },
            "other_info": "",
        }

    def parse(self, remarks_text: str) -> dict[str, dict[str, str]]:
        """備考欄の文字列を解析し、営業部署、エリアグループ、その他の情報を抽出する

        Args:
            remarks_text (str): 備考欄の文字列。

        Returns:
            Dict[str, Dict[str, str]]: 解析結果を格納した辞書
                - "request_type": 申請の種類("営業部傘下", "エリア", "その他")
                - "sales_department": 拠点内営業部名の情報を格納した辞書。
                    - "department_name": 拠点内営業部名,支店名・営業部名は含まない
                    - "branch_name": 支店名
                - "area_group": エリアグループの情報を格納した辞書
                    - "group_code": エリアグループコード
                    - "group_name": エリアグループ名
                    - "established_date": 設立日
                - "other_info": その他の情報
        """
        lines = [self._remove_leading_dot(line) for line in remarks_text.split("\n")]
        for line in lines:
            if any(keyword in line for keyword in ["変更", "廃止", "共通認証"]):
                self.result["other_info"] += line + "\n"
                continue

            if self.result["request_type"] == "":
                if "営業" in line:
                    self._process_sales_department(line)
                    continue

                #if "Gr" in line:
                if self._contains_gr(line):  # 全角半角Grを対象とする
                    self._process_area_group(line)
                    continue

            self.result["other_info"] += line + "\n"

        self.result["other_info"] = self.result["other_info"].strip()
        if self.result["request_type"] == "":
            self.result["request_type"] = "その他"
        return self.result

    def _remove_leading_dot(self, line: str) -> str:
        """行頭の全角ドット・を削除する。

        Args:
            line (str): 処理対象の行。

        Returns:
            str: 行頭のドットを削除した行。
        """
        return re.sub(r"^・", "", line)

    def _contains_gr(self, line: str) -> bool:
        """文字列内にGr(全角/半角)が含まれているかチェックする

        Args:
            line (str): チェック対象の文字列

        Returns:
            bool: Grが含まれている場合はTrue
        """
        # 全角のＧｒを半角に正規化
        normalized = unicodedata.normalize('NFKC', line)
        return 'Gr' in normalized

    def _process_sales_department(self, line: str) -> None:
        """営業部署の情報を処理し、解析結果に追加する。

        Args:
            line (str): 処理対象の行

        Notes:
            支店名と営業部署名を取得するための正規表現

            (.+?支店): 支店名。漢字、ひらがな、カタカナ、英数字を含む任意の文字列の後に「支店」が続く
            (.+?営業部): 営業部名。漢字、ひらがな、カタカナ、英数字を含む任意の文字列の後に「営業部」が続く
            ただし拠点内営業部名称の特性上、○○営業部判定には最短マッチ適用が必要になる

            (?:営業部|営業第[一二三四五六七八九十]+部): 営業部署名。「営業部」または「営業第」に続く漢数字と「部」
            ただし中間に「営業部」が組み込まれる可能性があり、最後の指定判別文字列にマッチするよう制御する

            備考欄解析によりマッチグループパターン全てに該当しないレコードに対しては
            request_type解析結果は格納されるが、department_name及びbranch_nameには値が格納されない
            つまり、department_name,branch_nameには両方とも値を持つもしくは両方とも空文字であるのどちらかになる
        """
        self.result["request_type"] = "営業部傘下"
        match = re.match(r"(.+?支店|.+?営業部)(営業部|(?:(?!営業部).)+営業部|営業第[一二三四五六七八九十]部)$", line)

        if match:
            log_msg("Regex match details:", LogLevel.DEBUG)
            log_msg(f"  Full match       : '{match.group(0)}'", LogLevel.DEBUG)
            log_msg(f"  Group 1 (code)   : '{match.group(1)}'", LogLevel.DEBUG)
            log_msg(f"  Group 2 (name)   : '{match.group(2)}'", LogLevel.DEBUG)

            self.result["sales_department"]["branch_name"] = match.group(1)
            self.result["sales_department"]["department_name"] = match.group(2)

        else:
            log_msg("Regex match failed:", LogLevel.DEBUG)
            log_msg(f"  Input text       : '{line}'", LogLevel.DEBUG)
            log_msg("Resetting area group values to empty", LogLevel.DEBUG)

        # 状況に関わらず other_infoに追加
        self.result["other_info"] += line + "\n"


    def _process_area_group(self, line: str) -> None:
        r"""エリアグループの情報を処理し、解析結果に追加する。

        Args:
            line (str): 処理対象の行。

        Notes:
            エリアグループコード、エリアグループ名、設立日を取得するための正規表現。
            完全一致(^...$)で以下のパターンをチェック:

            ^(\w{5})           : エリアグループコード。行頭から英数字5文字。
            [ \u3000]          : 半角または全角スペース。
            ([^\s]+?Gr)        : エリアグループ名。空白文字以外の1文字以上で「Gr」で終わる。
                                日本語や特殊文字を含む場合もあり。
            \s*(\(.*?\))?$     : 設立日。括弧内の任意の文字列。括弧は任意。行末まで。

        Examples:
            - "41002 東日本第一Gr"
            - "41012 グローバル財務戦略Gr (4/1新設)"
            - "A1B2C 営業部-1Gr"
        """
        self.result["request_type"] = "エリア"
        #match = re.match(r"^(\w{5})[ \u3000]([^\s]+?Gr)\s*(\(.*?\))?$", line)
        match = re.match(r"^(\w{5})[ \u3000]([^\s]+?(?:Gr|Ｇｒ))\s*(\(.*?\))?$", line)
        if match:
            log_msg("Regex match details:", LogLevel.DEBUG)
            log_msg(f"  Full match       : '{match.group(0)}'", LogLevel.DEBUG)
            log_msg(f"  Group 1 (code)   : '{match.group(1)}'", LogLevel.DEBUG)
            log_msg(f"  Group 2 (name)   : '{match.group(2)}'", LogLevel.DEBUG)
            log_msg(f"  Group 3 (date)   : '{match.group(3) if match.group(3) else ''}'", LogLevel.DEBUG)

            self.result["area_group"]["group_code"] = match.group(1)
            self.result["area_group"]["group_name"] = match.group(2)
            self.result["area_group"]["established_date"] = match.group(3)[1:-1] if match.group(3) else ""

        else:
            log_msg("Regex match failed:", LogLevel.DEBUG)
            log_msg(f"  Input text       : '{line}'", LogLevel.DEBUG)
            log_msg("Resetting area group values to empty", LogLevel.DEBUG)

        # 状況に関わらず other_infoに追加
        self.result["other_info"] += line + "\n"

