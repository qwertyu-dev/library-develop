import inspect
from functools import wraps
from pathlib import Path

from src.lib.common_utils.ibr_enums import LogLevel
from src.lib.common_utils.ibr_get_config import Config


def with_config(cls):
    # 使用例
    # from src.lib.common_utils.ibr_decorator_config import with_config
    # @with_config
    # class Aaaaaa:

    original_init = cls.__init__
    #print(f"Decorating class: {cls.__name__}")  # デバッグ用

    @wraps(cls)
    def new_init(self, *args, **kwargs) -> None:
        # クラスの実際のファイルパスを取得
        class_file = inspect.getfile(cls)
        config_path = Path(class_file).parent / 'package_config.toml'
        self.config = Config.load(config_path)

        # 元の__init__メソッドを呼び出す
        original_init(self, *args, **kwargs)

        #print(f"Initializing instance of: {cls.__name__}")  # デバッグ用
        #print(f"Looking for config at: {config_path}")  # デバッグ用
        #print(f"Config loaded for: {cls.__name__}")  # デバッグ用

    cls.__init__ = new_init
    return cls

def initialize_config(calling_module)-> tuple[Config|str]:
    """使用例

    SAMPLE:
    from src.lib.common_utils.ibr_decorator_config import initialize_config
    import sys
    config, log_msg = initialize_config(sys.modules[__name__])
    """
    # 呼び出し元のモジュールファイルのパスを取得
    caller_file = inspect.getfile(calling_module)
    config_path = Path(caller_file).parent / 'package_config.toml'
    return Config.load(config_path)

    #print(f"Looking for config at: {config_path}")  # デバッグ用
    #print(f"Config loaded for module: {calling_module.__name__}")  # デバッグ用
