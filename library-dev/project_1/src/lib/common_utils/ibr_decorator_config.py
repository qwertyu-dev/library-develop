from functools import wraps
from pathlib import Path
from src.lib.common_utils.ibr_get_config import Config
from src.lib.common_utils.ibr_enums import LogLevel

from functools import wraps
from pathlib import Path
from src.lib.common_utils.ibr_get_config import Config

import inspect
from pathlib import Path
from src.lib.common_utils.ibr_get_config import Config

import inspect
from functools import wraps
from pathlib import Path
from src.lib.common_utils.ibr_get_config import Config


def with_config(cls):
    print(f"Decorating class: {cls.__name__}")  # デバッグ用

    original_init = cls.__init__

    @wraps(cls)
    def new_init(self, *args, **kwargs):
        print(f"Initializing instance of: {cls.__name__}")  # デバッグ用

        # クラスの実際のファイルパスを取得
        class_file = inspect.getfile(cls)
        config_path = Path(class_file).parent / 'package_config.toml'

        print(f"Looking for config at: {config_path}")  # デバッグ用

        self.config = Config.load(config_path)
        print(f"Config loaded for: {cls.__name__}")  # デバッグ用

        # 元の__init__メソッドを呼び出す
        original_init(self, *args, **kwargs)

    cls.__init__ = new_init
    return cls


def initialize_config(calling_module):
    # 使用例
    # from src.lib.common_utils.ibr_decorator_config import initialize_config
    # import sys
    #
    # config, log_msg = initialize_config(sys.modules[__name__])

    # 呼び出し元のモジュールファイルのパスを取得
    caller_file = inspect.getfile(calling_module)
    config_path = Path(caller_file).parent / 'package_config.toml'

    print(f"Looking for config at: {config_path}")  # デバッグ用

    config = Config.load(config_path)
    print(f"Config loaded for module: {calling_module.__name__}")  # デバッグ用

    #return config, config.log_message
    return config


