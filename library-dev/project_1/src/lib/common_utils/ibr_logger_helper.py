from pprint import pformat
from typing import Any

def format_dict(data: dict[str, Any], indent: int = 2, width: int = 120) -> str:
    """辞書を読みやすい形式でフォーマットする"""
    return pformat(data, indent=indent, width=width)

def format_config(config: dict[str, Any]) -> str:
    """設定情報を読みやすい形式でフォーマットする"""
    return f"package_config:\n{format_dict(config)}"