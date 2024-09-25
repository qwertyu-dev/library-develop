import toml
from typing import  Any
import importlib

from src.lib.common_utils.ibr_enums import LogLevel
from src.lib.common_utils.ibr_logger_helper import format_config

# 動的importを行うので親Factoryのみimport
from .processor_factory import ProcessorFactory
from .model_factory import ModelFactory
from .file_configuration_factory import FileConfigurationFactory

class FactoryRegistryError(Exception):
    pass

# config共有
from src.lib.common_utils.ibr_decorator_config import with_config
#import sys
#from src.lib.common_utils.ibr_decorator_config import initialize_config
#config = initialize_config(sys.modules[__name__])

@with_config
class FactoryRegistry:
    def __init__(self, config: dict|None = None):
        # DI
        self.config = config or self.config
        self.log_msg = self.config.log_message

        # factory生成
        self.model_factories: dict[str, type[ModelFactory]] = self._load_factories('model_factory')
        self.processor_factories: dict[str, type[ProcessorFactory]] = self._load_factories('processor_factory')
        self.file_configuration_factories: dict[str, type[FileConfigurationFactory]] = self._load_factories('file_configuration_factory')
        self.log_msg(f"self.config.package_config: {format_config(self.config.package_config['processor_factory'])}", LogLevel.DEBUG)

    def _load_factories(self, factory_type: str) -> dict[str, Any]:
        factories = {}
        # 動的import定義はpackage_configに保有する前提
        for key, class_path in self.config.package_config[factory_type].items():
            try:
                # factory_typeに応じてサブClassを動的import
                module_name, class_name = class_path.rsplit('.', 1)
                module = importlib.import_module(module_name)
                factories[key] = getattr(module, class_name)
            except (ImportError, AttributeError) as e:
                err_msg = f"Error loading {factory_type} for {key}: {e}"
                self.log_msg(err_msg, LogLevel.INFO)
                raise
        return factories

    # カテゴリ別にfactory取得メソッド
    def get_processor_factory(self, key: str) -> type[ProcessorFactory]:
        return self.processor_factories.get(key)

    def get_model_factory(self, key: str) -> type[ModelFactory]:
        return self.model_factories.get(key)

    def get_file_configuration_factory(self, key: str) -> type[FileConfigurationFactory]:
        return self.file_configuration_factories.get(key)
