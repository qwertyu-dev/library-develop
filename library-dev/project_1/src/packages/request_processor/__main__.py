from src.lib.common_utils.ibr_enums import LogLevel
from src.lib.common_utils.ibr_dataframe_helper import tabulate_dataframe
from src.lib.common_utils.ibr_logger_helper import format_config

# config共有
from src.lib.common_utils.ibr_decorator_config import with_config

#import sys
#from src.lib.common_utils.ibr_decorator_config import initialize_config
#config = initialize_config(sys.modules[__name__])

from .processor_factory import (
    ProcessorFactory,
    JinjiProcessorFactory,
    KokukiProcessorFactory,
    KanrenProcessorFactory,
)

from .model_factory import (
    ModelFactory,
    JinjiModelFactory,
    KokukiModelFactory,
    KanrenModelFactory,
)

from .file_configration_factory import (
    FileConfigurationFactory,
    JinjiFileConfigurationFactory,
    KokukiFileConfigurationFactory,
    KanrenFileConfigurationFactory,
)

from .excel_processor import ExcelProcessor
from .data_validator import DataValidator

from .processor_interface import ProcessorChain

# パッケージ例外定義
class ExcelProcessorError(Exception):
    """package独自例外"""

@with_config
class RequestProcessExecutor:
    """アプリケーションのメインクラス。

    Excelファイルの処理を制御し、エラーハンドリングを行う。

    Attributes:
        定義情報: dict
    """
    def __init__(self, config: dict | None = None):
        """Mainクラスのコンストラクタ。設定の読み込みと初期化を行う。"""
        # DI config
        self.config = config or self.config
        # custom logger
        self.log_msg = self.config.log_message
        self.processor_chain = ProcessorChain()

        # processor factory
        self.processor_factories: dict[str, type[ProcessorFactory]] = {
            'jinji': JinjiProcessorFactory,
            'kokuki': KokukiProcessorFactory,
            'kanren': KanrenProcessorFactory,
        }

        # model factory
        self.model_factories: dict[str, type[ModelFactory]] = {
            'jinji': JinjiModelFactory,
            'kokuki': KokukiModelFactory,
            'kanren': KanrenModelFactory,
        }

        # file config factory
        self.file_configuration_factories: dict[str, type[FileConfigurationFactory]] = {
            'jinji': JinjiFileConfigurationFactory,
            'kokuki': KokukiFileConfigurationFactory,
            'kanren': KanrenFileConfigurationFactory,
        }

    def execute(self, department: str) -> None:
        """アプリケーションのメイン処理を実行する"""
        # 処理開始
        self.log_msg("IBRDEV-I-0000001")

        # model -> Validator
        model_factory = self.model_factories[department]()
        validation_model = model_factory.create_model()
        data_validator = DataValidator(self.config, validation_model)

        # pre/post要素
        # chain生成
        processor_factory = self.processor_factories[department]()
        pre_processor = processor_factory.create_pre_processor()
        post_processor = processor_factory.create_post_processor()
        processor_chain = ProcessorChain()
        processor_chain.pre_processors = pre_processor.chain_pre_process()
        processor_chain.post_processors = post_processor.chain_post_process()

        # Excel処理インスタンス生成
        file_configration_factory = self.file_configuration_factories[department](self.config)
        excel_processor = ExcelProcessor(self.config, file_configration_factory)

        self.log_msg(f'Factory Model: {model_factory}', LogLevel.INFO)
        self.log_msg(f'Factory FileConfig: {file_configration_factory}', LogLevel.INFO)
        self.log_msg(f'Factory Processor: {processor_factory}', LogLevel.INFO)
        self.log_msg(f'Instance Validation: {validation_model}', LogLevel.INFO)
        self.log_msg(f'Instance Validator: {data_validator}', LogLevel.INFO)
        self.log_msg(f'Instance PreProcessor: {pre_processor}', LogLevel.INFO)
        self.log_msg(f'Instance PostProcessor: {post_processor}', LogLevel.INFO)
        self.log_msg(f'Instance Chain PreProcessor chain: {processor_chain.pre_processors}', LogLevel.INFO)
        self.log_msg(f'Instance Chain PostProcessor chain: {processor_chain.post_processors}', LogLevel.INFO)
        self.log_msg(f'Instance ExcelProcessoer: {excel_processor}', LogLevel.INFO)

        # Excelファイル読み込み
        _df, cols = excel_processor.load()

        # 対象外データ
        if _df.empty:
            # 処理はバイパスして継続する
            err_msg = "Target DataFrame is empty..."
            self.log_msg(err_msg, LogLevel.INFO)
            formatted_config = format_config(self.config.package_config)
            self.log_msg(f"Error in column_map: \n{formatted_config}", LogLevel.ERROR)
            return

        # 前処理
        ## 日本語Column→PythonColumn変換
        ## 部店,課Gr申請凸凹チェック
        ## 部店,課Gr申請リクエスト更新明細チェック(存在,AAA反映日相関)
        ## REF FIND処理(申請相関)
        _df = processor_chain.execute_pre_processor(_df)

        # Validator/整合性チェク
        data_validator.validate(_df)
        ## エラーがある場合は処理中断
        #if data_validator.error_manager.has_errors():
        #    return

        # 後処理
        ## 統合レイアウト変換
        ## 受付向けの編集処理(ULID,申請部署情報)
        ## 動的ブラックリストチェック
        _df = processor_chain.execute_post_processor(_df)

        ## ファイルのマージ(jinji, kokuki, kanren処理結果)

        # 処理終了ログ
        self.log_msg(f'\n{tabulate_dataframe(_df)}', LogLevel.INFO)
        self.log_msg("IBRDEV-I-0000002")

if __name__ == '__main__':
    # 一括申請実行
    executor = RequestProcessExecutor()
    processes = [
        'jinji',
        'kokuki',
        'kanren',
        ]
    for process in processes:
        executor.execute(process)
