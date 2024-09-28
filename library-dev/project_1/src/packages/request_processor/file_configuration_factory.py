from pathlib import Path

# config共有
from src.lib.common_utils.ibr_decorator_config import with_config
#import sys
#from src.lib.common_utils.ibr_decorator_config import initialize_config
#config = initialize_config(sys.modules[__name__])

class FileConfigurationFactory():
    def create_file_path(self) -> Path:
        pass

    def create_sheet_name(self) -> str:
        pass

@with_config
class JinjiFileConfigurationFactory(FileConfigurationFactory):
    def __init__(self, config: dict|None = None):
        # DI config
        self.config = config or self.config

    def create_file_pattern(self) -> Path:
        base_path = Path(self.config.common_config.get('optional_path', {}).get('SHARE_RECEIVE_PATH', ''))
        pattern = self.config.package_config.get('excel_definition', {}).get('UPDATE_RECORD_JINJI', '')
        return list(base_path.glob(pattern))

        # listを返すように変更
        #return list(
        #    Path(
        #        f"{self.config.common_config.get('optional_path', {}).get('SHARE_RECEIVE_PATH','')}",
        #    ).glob(
        #        f"{self.config.package_config.get('excel_definition', {}).get('UPDATE_RECORD_JINJI', '')}",
        #    )
        #)

    def create_sheet_name(self) -> str:
        return self.config.package_config.get('excel_definition', {}).get('UPDATE_RECORD_JINJI_SHEET_NAME', '')


@with_config
class KokukiFileConfigurationFactory(FileConfigurationFactory):
    def __init__(self, config: dict|None = None):
        # DI config
        self.config = config or self.config

    #def create_file_path(self) -> Path:
    def create_file_pattern(self) -> Path:
        base_path = Path(self.config.common_config.get('optional_path', {}).get('SHARE_RECEIVE_PATH', ''))
        pattern = self.config.package_config.get('excel_definition', {}).get('UPDATE_RECORD_KOKUKI', '')
        return list(base_path.glob(pattern))

        ## listを返すように変更
        #return list(Path(
        #        f"{self.config.common_config.get('optional_path', {}).get('SHARE_RECEIVE_PATH','')}",
        #    ).glob(
        #        f"{self.config.package_config.get('excel_definition', {}).get('UPDATE_RECORD_KOKUKI', '')}",
        #    )
        #)

    def create_sheet_name(self) -> str:
        return self.config.package_config.get('excel_definition', {}).get('UPDATE_RECORD_KOKUKI_SHEET_NAME', '')

@with_config
class KanrenFileConfigurationFactory(FileConfigurationFactory):
    def __init__(self, config: dict|None = None):
        # DI config
        self.config = config or self.config

    def create_file_pattern(self) -> Path:
        base_path = Path(self.config.common_config.get('optional_path', {}).get('SHARE_RECEIVE_PATH', ''))
        pattern = self.config.package_config.get('excel_definition', {}).get('UPDATE_RECORD_KANREN', '')
        return list(base_path.glob(pattern))

        #return list(
        #    Path(
        #        f"{self.config.common_config.get('optional_path', {}).get('SHARE_RECEIVE_PATH','')}",
        #    ).glob(
        #        f"{self.config.package_config.get('excel_definition', {}).get('UPDATE_RECORD_KANREN', '')}",
        #    )
        #)

    def create_sheet_name(self) -> str:
        return self.config.package_config.get('excel_definition', {}).get('UPDATE_RECORD_KANREN_SHEET_NAME', '')
