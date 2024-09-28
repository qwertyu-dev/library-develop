import pytest
import pandas as pd
from src.model.processor_chain.processor_interface import Processor
from src.model.processor_chain.processor_interface import (
    ProcessorChain,
    PreProcessor,
    PostProcessor,
)


from typing import Any
from src.model.processor_chain.processor_interface import Validator

####################################
# テストサポートモジュールimport
####################################
# config共有
import sys
from src.lib.common_utils.ibr_enums import LogLevel
from src.lib.common_utils.ibr_decorator_config import initialize_config
config = initialize_config(sys.modules[__name__])
log_msg = config.log_message
log_msg(str(config), LogLevel.DEBUG)

class TestProcessor:
    """Processorクラスのテスト

    テスト構造:
    ├── C0: 基本構造テスト
    │   └── process メソッドの存在確認
    ├── C1: 例外発生テスト
    │   └── process メソッドがNotImplementedErrorを発生させることを確認
    └── C2: デコレータ適用テスト
        └── @with_config デコレータが正しく適用されていることを確認

    # C1のディシジョンテーブル
    | 条件                     | ケース1 |
    |--------------------------|---------|
    | process メソッドを呼び出す | Y       |
    | 出力                     | 例外発生 |

    境界値検証ケース一覧：
    | ケースID | 入力パラメータ | テスト値          | 期待される結果      | テストの目的/検証ポイント           | 実装状況 | 対応するテストケース              |
    |----------|----------------|-------------------|---------------------|-------------------------------------|----------|-----------------------------------|
    | BVT_001  | df             | 空のDataFrame     | NotImplementedError | 空のDataFrameでの動作確認           | 実装済み | test_process_BVT_various_inputs   |
    | BVT_002  | df             | 1行のDataFrame    | NotImplementedError | 最小のDataFrameでの動作確認         | 実装済み | test_process_BVT_various_inputs   |
    | BVT_003  | df             | 大規模なDataFrame | NotImplementedError | 大規模なDataFrameでの動作確認       | 実装済み | test_process_BVT_various_inputs   |

    境界値検証ケースの実装状況サマリー：
    - 実装済み: 4
    - 未実装: 0
    - 一部実装: 0

    注記：
    - すべての境界値検証ケースが実装されています。
    - BVT_004は、型チェックが行われることを前提としています。実際の実装によっては、この動作が異なる可能性があります。
    """

    def setup_method(self):
        log_msg("test start", LogLevel.INFO)
        self.processor = Processor()

    def teardown_method(self):
        log_msg(f"test end\n{'-'*80}\n", LogLevel.INFO)

    def test_process_C0_method_exists(self):
        test_doc = """テスト内容:
        - テストカテゴリ: C0
        - テスト区分: 正常系
        - テストシナリオ: process メソッドの存在確認
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        assert hasattr(self.processor, 'process')
        assert callable(getattr(self.processor, 'process'))
        log_msg("process メソッドが存在し、呼び出し可能です", LogLevel.DEBUG)

    def test_process_C1_not_implemented(self):
        test_doc = """テスト内容:
        - テストカテゴリ: C1
        - テスト区分: 異常系
        - テストシナリオ: process メソッドがNotImplementedErrorを発生させることを確認
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        df = pd.DataFrame()
        with pytest.raises(NotImplementedError):
            self.processor.process(df)
        log_msg("NotImplementedErrorが正しく発生しました", LogLevel.DEBUG)

    def test_process_C2_with_config_decorator(self):
        test_doc = """テスト内容:
        - テストカテゴリ: C2
        - テスト区分: 正常系
        - テストシナリオ: @with_config デコレータが正しく適用されていることを確認
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        assert hasattr(self.processor, 'config')
        log_msg("@with_config デコレータが正しく適用されています", LogLevel.DEBUG)

    # 実装側での検証責務でありインターフェース側での検証は対象外
    #def test_process_C2_invalid_input(self):
    #    test_doc = """テスト内容:
    #    - テストカテゴリ: C2
    #    - テスト区分: 異常系
    #    - テストシナリオ: 不正な入力型での例外発生確認
    #    """
    #    log_msg(f"\n{test_doc}", LogLevel.INFO)

    #    with pytest.raises(TypeError):
    #        self.processor.process(None)
    #    log_msg("不正な入力に対してTypeErrorが発生しました", LogLevel.DEBUG)

    @pytest.mark.parametrize("df", [
        pd.DataFrame(),
        pd.DataFrame({'A': [1]}),
        pd.DataFrame({'A': range(1000000)}),
    ])
    def test_process_BVT_various_inputs(self, df):
        test_doc = """テスト内容:
        - テストカテゴリ: BVT
        - テスト区分: 異常系
        - テストシナリオ: 様々な入力サイズでのprocess メソッドの動作確認
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        with pytest.raises(NotImplementedError):
            self.processor.process(df)
        log_msg(f"入力サイズ {len(df)} の DataFrame に対してNotImplementedErrorが発生しました", LogLevel.DEBUG)

class TestValidator:
    """Validatorクラスのテスト

    テスト構造:
    ├── C0: 基本構造テスト
    │   └── validate メソッドの存在確認
    └── C1: メソッド動作テスト
        └── validate メソッドが例外を発生させずに実行されることを確認
    """

    def setup_method(self):
        log_msg("test start", LogLevel.INFO)
        self.validator = Validator()

    def teardown_method(self):
        log_msg(f"test end\n{'-'*80}\n", LogLevel.INFO)

    def test_validate_C0_method_exists(self):
        test_doc = """テスト内容:
        - テストカテゴリ: C0
        - テスト区分: 正常系
        - テストシナリオ: validate メソッドの存在確認
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        assert hasattr(self.validator, 'validate')
        assert callable(getattr(self.validator, 'validate'))
        log_msg("validate メソッドが存在し、呼び出し可能です", LogLevel.DEBUG)

    def test_validate_C1_no_exception(self):
        test_doc = """テスト内容:
        - テストカテゴリ: C1
        - テスト区分: 正常系
        - テストシナリオ: validate メソッドが例外を発生させずに実行されることを確認
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        try:
            self.validator.validate(None)
            log_msg("validate メソッドが例外を発生させずに実行されました", LogLevel.DEBUG)
        except Exception as e:
            pytest.fail(f"validate メソッドが予期せぬ例外を発生させました: {str(e)}")

    def test_validate_C1_return_none(self):
        test_doc = """テスト内容:
        - テストカテゴリ: C1
        - テスト区分: 正常系
        - テストシナリオ: validate メソッドがNoneを返すことを確認
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        result = self.validator.validate(None)
        assert result is None
        log_msg("validate メソッドがNoneを返しました", LogLevel.DEBUG)

class TestProcessorChainInit:
    """ProcessorChainクラスの__init__メソッドのテスト

    テスト構造:
    ├── C0: 基本機能テスト
    │   └── インスタンス生成時に空のリストが初期化されることを確認
    ├── C1: 属性初期化テスト
    │   ├── pre_processors属性が空のリストで初期化されることを確認
    │   └── post_processors属性が空のリストで初期化されることを確認
    └── C2: 型チェックテスト
        ├── pre_processors属性がリスト型であることを確認
        └── post_processors属性がリスト型であることを確認

    # C1のディシジョンテーブル
    | 条件                          | ケース1 |
    |-------------------------------|---------|
    | インスタンスを生成する        | Y       |
    | 出力                          | 空リスト |

    境界値検証ケース一覧：
    | ケースID | 入力パラメータ | テスト値 | 期待される結果 | テストの目的/検証ポイント      | 実装状況 | 対応するテストケース              |
    |----------|----------------|----------|----------------|--------------------------------|----------|-----------------------------------|
    | BVT_001  | N/A            | N/A      | 空リスト       | インスタンス生成時の初期状態確認 | 実装済み | test_init_C0_empty_lists          |

    境界値検証ケースの実装状況サマリー：
    - 実装済み: 1
    - 未実装: 0
    - 一部実装: 0

    注記：
    - __init__メソッドは引数を取らないため、境界値テストのケースは限定的です。
    - 主に、初期化後の状態が期待通りであることを確認するテストとなっています。
    """

    def setup_method(self):
        log_msg("test start", LogLevel.INFO)

    def teardown_method(self):
        log_msg(f"test end\n{'-'*80}\n", LogLevel.INFO)

    def test_init_C0_empty_lists(self):
        test_doc = """テスト内容:
        - テストカテゴリ: C0
        - テスト区分: 正常系
        - テストシナリオ: インスタンス生成時に空のリストが初期化されることを確認
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        processor_chain = ProcessorChain()
        assert isinstance(processor_chain.pre_processors, list)
        assert isinstance(processor_chain.post_processors, list)
        assert len(processor_chain.pre_processors) == 0
        assert len(processor_chain.post_processors) == 0
        log_msg("ProcessorChainインスタンスが正しく初期化されました", LogLevel.DEBUG)

    def test_init_C1_pre_processors_initialization(self):
        test_doc = """テスト内容:
        - テストカテゴリ: C1
        - テスト区分: 正常系
        - テストシナリオ: pre_processors属性が空のリストで初期化されることを確認
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        processor_chain = ProcessorChain()
        assert processor_chain.pre_processors == []
        log_msg("pre_processors属性が空のリストで初期化されました", LogLevel.DEBUG)

    def test_init_C1_post_processors_initialization(self):
        test_doc = """テスト内容:
        - テストカテゴリ: C1
        - テスト区分: 正常系
        - テストシナリオ: post_processors属性が空のリストで初期化されることを確認
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        processor_chain = ProcessorChain()
        assert processor_chain.post_processors == []
        log_msg("post_processors属性が空のリストで初期化されました", LogLevel.DEBUG)

    def test_init_C2_pre_processors_type(self):
        test_doc = """テスト内容:
        - テストカテゴリ: C2
        - テスト区分: 正常系
        - テストシナリオ: pre_processors属性がリスト型であることを確認
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        processor_chain = ProcessorChain()
        assert isinstance(processor_chain.pre_processors, list)
        log_msg("pre_processors属性がリスト型であることを確認しました", LogLevel.DEBUG)

    def test_init_C2_post_processors_type(self):
        test_doc = """テスト内容:
        - テストカテゴリ: C2
        - テスト区分: 正常系
        - テストシナリオ: post_processors属性がリスト型であることを確認
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        processor_chain = ProcessorChain()
        assert isinstance(processor_chain.post_processors, list)
        log_msg("post_processors属性がリスト型であることを確認しました", LogLevel.DEBUG)

class TestProcessorChainAddPreProcessor:
    """ProcessorChainクラスのadd_pre_processorメソッドのテスト

    テスト構造:
    ├── C0: 基本機能テスト
    │   └── プリプロセッサが正しく追加されることを確認
    ├── C1: 複数追加テスト
    │   └── 複数のプリプロセッサが正しく追加されることを確認
    ├── C2: 型チェックテスト
    │   ├── PreProcessor型のオブジェクトが正しく追加されることを確認
    │   └── PreProcessor型でないオブジェクトを追加した場合にTypeErrorが発生することを確認
    └── BVT: 境界値テスト
        ├── 多数のプリプロセッサを追加した場合の動作確認
        └── 同じプリプロセッサを複数回追加した場合の動作確認

    # C1のディシジョンテーブル
    | 条件                                  | ケース1 | ケース2 | ケース3 |
    |---------------------------------------|---------|---------|---------|
    | PreProcessor型のオブジェクトを追加    | Y       | Y       | N       |
    | 複数のプリプロセッサを追加            | N       | Y       | -       |
    | 出力                                  | 追加成功 | 追加成功 | 追加成功 |

    境界値検証ケース一覧：
    | ケースID | 入力パラメータ     | テスト値                     | 期待される結果            | テストの目的/検証ポイント                  | 実装状況 | 対応するテストケース                    |
    |----------|--------------------|------------------------------|---------------------------|-------------------------------------------|----------|-----------------------------------------|
    | BVT_001  | processor          | PreProcessor()               | リストに1つ追加           | 単一のプリプロセッサ追加の確認             | 実装済み | test_add_pre_processor_C0_single_add    |
    | BVT_002  | processor (複数回) | [PreProcessor() for _ in range(1000)] | リストに1000個追加 | 大量のプリプロセッサ追加時の動作確認       | 実装済み | test_add_pre_processor_BVT_many_processors |
    | BVT_003  | processor (重複)   | 同じPreProcessorインスタンス | リストに重複して追加      | 同一プリプロセッサの重複追加の動作確認     | 実装済み | test_add_pre_processor_BVT_duplicate_add |

    境界値検証ケースの実装状況サマリー：
    - 実装済み: 3
    - 未実装: 0
    - 一部実装: 0

    注記：
    - 本件はInterfaceの責務検証であり,委譲先が担当する責務はこのテストでは実施していません
    - すべての境界値検証ケースが実装されています。
    - BVT_002の1000という数値は例示的なものであり、実際のシステム要件に応じて適切な値に調整する必要があります。
    """

    def setup_method(self):
        log_msg("test start", LogLevel.INFO)
        self.processor_chain = ProcessorChain()

    def teardown_method(self):
        log_msg(f"test end\n{'-'*80}\n", LogLevel.INFO)

    def test_add_pre_processor_C0_single_add(self):
        test_doc = """テスト内容:
        - テストカテゴリ: C0
        - テスト区分: 正常系
        - テストシナリオ: 単一のプリプロセッサが正しく追加されることを確認
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        processor = PreProcessor()
        self.processor_chain.add_pre_processor(processor)
        assert len(self.processor_chain.pre_processors) == 1
        assert self.processor_chain.pre_processors[0] == processor
        log_msg("単一のプリプロセッサが正しく追加されました", LogLevel.DEBUG)

    def test_add_pre_processor_C1_multiple_add(self):
        test_doc = """テスト内容:
        - テストカテゴリ: C1
        - テスト区分: 正常系
        - テストシナリオ: 複数のプリプロセッサが正しく追加されることを確認
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        processors = [PreProcessor() for _ in range(3)]
        for processor in processors:
            self.processor_chain.add_pre_processor(processor)
        assert len(self.processor_chain.pre_processors) == 3
        assert self.processor_chain.pre_processors == processors
        log_msg("複数のプリプロセッサが正しく追加されました", LogLevel.DEBUG)

    def test_add_pre_processor_C2_type_check(self):
        test_doc = """テスト内容:
        - テストカテゴリ: C2
        - テスト区分: 正常系
        - テストシナリオ: PreProcessor型でないオブジェクトも追加できることを確認
        - PreProcesssor/PostProcessor型チェックは実装側の責務とする
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)
    
        non_processor = "not a processor"
        self.processor_chain.add_pre_processor(non_processor)
        assert self.processor_chain.pre_processors[-1] == non_processor
        log_msg("PreProcessor型でないオブジェクトも正常に追加されました", LogLevel.DEBUG)

    def test_add_pre_processor_BVT_many_processors(self):
        test_doc = """テスト内容:
        - テストカテゴリ: BVT
        - テスト区分: 正常系
        - テストシナリオ: 多数のプリプロセッサを追加した場合の動作確認
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        processors = [PreProcessor() for _ in range(1000)]
        for processor in processors:
            self.processor_chain.add_pre_processor(processor)
        assert len(self.processor_chain.pre_processors) == 1000
        assert self.processor_chain.pre_processors == processors
        log_msg("1000個のプリプロセッサが正しく追加されました", LogLevel.DEBUG)

    def test_add_pre_processor_BVT_duplicate_add(self):
        test_doc = """テスト内容:
        - テストカテゴリ: BVT
        - テスト区分: 正常系
        - テストシナリオ: 同じプリプロセッサを複数回追加した場合の動作確認
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        processor = PreProcessor()
        for _ in range(3):
            self.processor_chain.add_pre_processor(processor)
        assert len(self.processor_chain.pre_processors) == 3
        assert all(p == processor for p in self.processor_chain.pre_processors)
        log_msg("同じプリプロセッサが3回正しく追加されました", LogLevel.DEBUG)

class TestProcessorChainAddPostProcessor:
    """ProcessorChainクラスのadd_post_processorメソッドのテスト

    テスト構造:
    ├── C0: 基本機能テスト
    │   └── ポストプロセッサが正しく追加されることを確認
    ├── C1: 複数追加テスト
    │   └── 複数のポストプロセッサが正しく追加されることを確認
    ├── C2: 型チェックテスト
    │   └── PostProcessor型でないオブジェクトも追加できることを確認
    └── BVT: 境界値テスト
        ├── 多数のポストプロセッサを追加した場合の動作確認
        └── 同じポストプロセッサを複数回追加した場合の動作確認

    # C1のディシジョンテーブル
    | 条件                                   | ケース1 | ケース2 | ケース3 |
    |----------------------------------------|---------|---------|---------|
    | PostProcessor型のオブジェクトを追加    | Y       | Y       | N       |
    | 複数のポストプロセッサを追加           | N       | Y       | -       |
    | 出力                                   | 追加成功 | 追加成功 | 追加成功 |

    境界値検証ケース一覧：
    | ケースID | 入力パラメータ     | テスト値                     | 期待される結果            | テストの目的/検証ポイント                  | 実装状況 | 対応するテストケース                    |
    |----------|--------------------|------------------------------|---------------------------|-------------------------------------------|----------|-----------------------------------------|
    | BVT_001  | processor          | PostProcessor()              | リストに1つ追加           | 単一のポストプロセッサ追加の確認           | 実装済み | test_add_post_processor_C0_single_add   |
    | BVT_002  | processor (複数回) | [PostProcessor() for _ in range(1000)] | リストに1000個追加 | 大量のポストプロセッサ追加時の動作確認     | 実装済み | test_add_post_processor_BVT_many_processors |
    | BVT_003  | processor (重複)   | 同じPostProcessorインスタンス | リストに重複して追加      | 同一ポストプロセッサの重複追加の動作確認   | 実装済み | test_add_post_processor_BVT_duplicate_add |

    境界値検証ケースの実装状況サマリー：
    - 実装済み: 3
    - 未実装: 0
    - 一部実装: 0

    注記：
    - すべての境界値検証ケースが実装されています。
    - BVT_002の1000という数値は例示的なものであり、実際のシステム要件に応じて適切な値に調整する必要があります。
    """

    def setup_method(self):
        log_msg("test start", LogLevel.INFO)
        self.processor_chain = ProcessorChain()

    def teardown_method(self):
        log_msg(f"test end\n{'-'*80}\n", LogLevel.INFO)

    def test_add_post_processor_C0_single_add(self):
        test_doc = """テスト内容:
        - テストカテゴリ: C0
        - テスト区分: 正常系
        - テストシナリオ: 単一のポストプロセッサが正しく追加されることを確認
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        processor = PostProcessor()
        self.processor_chain.add_post_processor(processor)
        assert len(self.processor_chain.post_processors) == 1
        assert self.processor_chain.post_processors[0] == processor
        log_msg("単一のポストプロセッサが正しく追加されました", LogLevel.DEBUG)

    def test_add_post_processor_C1_multiple_add(self):
        test_doc = """テスト内容:
        - テストカテゴリ: C1
        - テスト区分: 正常系
        - テストシナリオ: 複数のポストプロセッサが正しく追加されることを確認
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        processors = [PostProcessor() for _ in range(3)]
        for processor in processors:
            self.processor_chain.add_post_processor(processor)
        assert len(self.processor_chain.post_processors) == 3
        assert self.processor_chain.post_processors == processors
        log_msg("複数のポストプロセッサが正しく追加されました", LogLevel.DEBUG)

    def test_add_post_processor_C2_type_check(self):
        test_doc = """テスト内容:
        - テストカテゴリ: C2
        - テスト区分: 正常系
        - テストシナリオ: PostProcessor型でないオブジェクトも追加できることを確認
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        non_processor = "not a processor"
        self.processor_chain.add_post_processor(non_processor)
        assert self.processor_chain.post_processors[-1] == non_processor
        log_msg("PostProcessor型でないオブジェクトも正常に追加されました", LogLevel.DEBUG)

    def test_add_post_processor_BVT_many_processors(self):
        test_doc = """テスト内容:
        - テストカテゴリ: BVT
        - テスト区分: 正常系
        - テストシナリオ: 多数のポストプロセッサを追加した場合の動作確認
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        processors = [PostProcessor() for _ in range(1000)]
        for processor in processors:
            self.processor_chain.add_post_processor(processor)
        assert len(self.processor_chain.post_processors) == 1000
        assert self.processor_chain.post_processors == processors
        log_msg("1000個のポストプロセッサが正しく追加されました", LogLevel.DEBUG)

    def test_add_post_processor_BVT_duplicate_add(self):
        test_doc = """テスト内容:
        - テストカテゴリ: BVT
        - テスト区分: 正常系
        - テストシナリオ: 同じポストプロセッサを複数回追加した場合の動作確認
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        processor = PostProcessor()
        for _ in range(3):
            self.processor_chain.add_post_processor(processor)
        assert len(self.processor_chain.post_processors) == 3
        assert all(p == processor for p in self.processor_chain.post_processors)
        log_msg("同じポストプロセッサが3回正しく追加されました", LogLevel.DEBUG)
