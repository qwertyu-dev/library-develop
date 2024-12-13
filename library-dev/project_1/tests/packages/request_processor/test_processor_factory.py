# config共有
import sys

import pytest

from src.lib.common_utils.ibr_decorator_config import initialize_config
from src.lib.common_utils.ibr_enums import LogLevel
from src.model.processor_chain.processor_interface import PostProcessor, PreProcessor
from src.packages.request_processor.jinji_processor import JinjiPostProcessor, JinjiPreProcessor
from src.packages.request_processor.kanren_with_processor import KanrenWithPostProcessor, KanrenWithPreProcessor
from src.packages.request_processor.kanren_without_processor import KanrenWithoutPostProcessor, KanrenWithoutPreProcessor
from src.packages.request_processor.kokuki_processor import KokukiPostProcessor, KokukiPreProcessor
from src.packages.request_processor.processor_factory import (
    JinjiProcessorFactory,
    KanrenWithProcessorFactory,
    KanrenWithoutProcessorFactory,
    KokukiProcessorFactory,
    ProcessorFactory,
)

config = initialize_config(sys.modules[__name__])
log_msg = config.log_message
log_msg(str(config), LogLevel.DEBUG)

class TestProcessorFactory:
    """ProcessorFactoryクラスのテスト

    テスト構造:
    ├── C0: 基本機能テスト
    │   ├── create_pre_processor メソッドが NotImplementedError を発生させることを確認
    │   └── create_post_processor メソッドが NotImplementedError を発生させることを確認

    # C1のディシジョンテーブル
    C1テストは適用されないため、ディシジョンテーブルはありません。

    境界値検証ケース一覧:g
    このクラスには境界値テストを適用する数値パラメータや範囲を持つ入力がないため、
    境界値検証ケースはありません。
    """

    def setup_method(self):
        log_msg("test start", LogLevel.INFO)

    def teardown_method(self):
        log_msg(f"test end\n{'-'*80}\n", LogLevel.INFO)

    @pytest.fixture()
    def processor_factory(self):
        return ProcessorFactory()

    def test_create_pre_processor_C0_not_implemented(self, processor_factory):
        test_doc = """
        テスト区分: UT
        テストカテゴリ: C0
        テスト区分: 異常系
        テストシナリオ: create_pre_processorメソッドがNotImplementedErrorを発生させることを確認
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        with pytest.raises(NotImplementedError):
            processor_factory.create_pre_processor()

    def test_create_post_processor_C0_not_implemented(self, processor_factory):
        test_doc = """
        テスト区分: UT
        テストカテゴリ: C0
        テスト区分: 異常系
        テストシナリオ: create_post_processorメソッドがNotImplementedErrorを発生させることを確認
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        with pytest.raises(NotImplementedError):
            processor_factory.create_post_processor()

class TestJinjiProcessorFactory:
    """JinjiProcessorFactoryクラスのテスト

    テスト構造:
    ├── C0: 基本機能テスト
    │   ├── create_pre_processor メソッドが JinjiPreProcessor インスタンスを返し、PreProcessor を継承していることを確認
    │   └── create_post_processor メソッドが JinjiPostProcessor インスタンスを返し、PostProcessor を継承していることを確認

    # C1のディシジョンテーブル
    C1テストは適用されないため、ディシジョンテーブルはありません。

    境界値検証ケース一覧:g
    このクラスには境界値テストを適用する数値パラメータや範囲を持つ入力がないため、
    境界値検証ケースはありません。
    """

    def setup_method(self):
        log_msg("test start", LogLevel.INFO)

    def teardown_method(self):
        log_msg(f"test end\n{'-'*80}\n", LogLevel.INFO)

    @pytest.fixture()
    def jinji_processor_factory(self):
        return JinjiProcessorFactory()

    def test_create_pre_processor_C0_returns_jinji_pre_processor(self, jinji_processor_factory):
        test_doc = """
        テスト区分: UT
        テストカテゴリ: C0
        テスト区分: 正常系
        テストシナリオ: create_pre_processorメソッドがJinjiPreProcessorインスタンスを返し、PreProcessorを継承していることを確認
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        result = jinji_processor_factory.create_pre_processor()
        assert isinstance(result, JinjiPreProcessor), f"Expected JinjiPreProcessor, got {type(result)}"
        assert isinstance(result, PreProcessor), "JinjiPreProcessor does not inherit from PreProcessor"
        assert hasattr(result, 'chain_pre_process'), "JinjiPreProcessor does not have 'chain_pre_process' method"
        assert isinstance(result.chain_pre_process(), list), "chain_pre_process method should return a list"

    def test_create_post_processor_C0_returns_jinji_post_processor(self, jinji_processor_factory):
        test_doc = """
        テスト区分: UT
        テストカテゴリ: C0
        テスト区分: 正常系
        テストシナリオ: create_post_processorメソッドがJinjiPostProcessorインスタンスを返し、PostProcessorを継承していることを確認
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        result = jinji_processor_factory.create_post_processor()
        assert isinstance(result, JinjiPostProcessor), f"Expected JinjiPostProcessor, got {type(result)}"
        assert isinstance(result, PostProcessor), "JinjiPostProcessor does not inherit from PostProcessor"
        assert hasattr(result, 'chain_post_process'), "JinjiPostProcessor does not have 'chain_post_process' method"
        assert isinstance(result.chain_post_process(), list), "chain_post_process method should return a list"

class TestKokukiProcessorFactory:
    """KokukiProcessorFactoryクラスのテスト

    テスト構造:
    ├── C0: 基本機能テスト
    │   ├── create_pre_processor メソッドが KokukiPreProcessor インスタンスを返し、PreProcessor を継承していることを確認
    │   └── create_post_processor メソッドが KokukiPostProcessor インスタンスを返し、PostProcessor を継承していることを確認

    # C1のディシジョンテーブル
    C1テストは適用されないため、ディシジョンテーブルはありません。

    境界値検証ケース一覧:g
    このクラスには境界値テストを適用する数値パラメータや範囲を持つ入力がないため、
    境界値検証ケースはありません。
    """

    def setup_method(self):
        log_msg("test start", LogLevel.INFO)

    def teardown_method(self):
        log_msg(f"test end\n{'-'*80}\n", LogLevel.INFO)

    @pytest.fixture()
    def kokuki_processor_factory(self):
        return KokukiProcessorFactory()

    def test_create_pre_processor_C0_returns_kokuki_pre_processor(self, kokuki_processor_factory):
        test_doc = """
        テスト区分: UT
        テストカテゴリ: C0
        テスト区分: 正常系
        テストシナリオ: create_pre_processorメソッドがKokukiPreProcessorインスタンスを返し、PreProcessorを継承していることを確認
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        result = kokuki_processor_factory.create_pre_processor()
        assert isinstance(result, KokukiPreProcessor), f"Expected KokukiPreProcessor, got {type(result)}"
        assert isinstance(result, PreProcessor), "KokukiPreProcessor does not inherit from PreProcessor"
        assert hasattr(result, 'chain_pre_process'), "KokukiPreProcessor does not have 'chain_pre_process' method"
        assert isinstance(result.chain_pre_process(), list), "chain_pre_process method should return a list"

    def test_create_post_processor_C0_returns_kokuki_post_processor(self, kokuki_processor_factory):
        test_doc = """
        テスト区分: UT
        テストカテゴリ: C0
        テスト区分: 正常系
        テストシナリオ: create_post_processorメソッドがKokukiPostProcessorインスタンスを返し、PostProcessorを継承していることを確認
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        result = kokuki_processor_factory.create_post_processor()
        assert isinstance(result, KokukiPostProcessor), f"Expected KokukiPostProcessor, got {type(result)}"
        assert isinstance(result, PostProcessor), "KokukiPostProcessor does not inherit from PostProcessor"
        assert hasattr(result, 'chain_post_process'), "KokukiPostProcessor does not have 'chain_post_process' method"
        assert isinstance(result.chain_post_process(), list), "chain_post_process method should return a list"

class TestKanrenWithProcessorFactory:
    """KanrenProcessorFactoryクラスのテスト

    テスト構造:
    ├── C0: 基本機能テスト
    │   ├── create_pre_processor メソッドが KanrenWitPreProcessor インスタンスを返し、PreProcessor を継承していることを確認
    │   └── create_post_processor メソッドが KanrenWithPostProcessor インスタンスを返し、PostProcessor を継承していることを確認

    # C1のディシジョンテーブル
    C1テストは適用されないため、ディシジョンテーブルはありません。

    境界値検証ケース一覧:g
    このクラスには境界値テストを適用する数値パラメータや範囲を持つ入力がないため、
    境界値検証ケースはありません。
    """

    def setup_method(self):
        log_msg("test start", LogLevel.INFO)

    def teardown_method(self):
        log_msg(f"test end\n{'-'*80}\n", LogLevel.INFO)

    @pytest.fixture()
    def kanren_processor_factory(self):
        return KanrenWithProcessorFactory()

    def test_create_pre_processor_C0_returns_kanren_pre_processor(self, kanren_processor_factory):
        test_doc = """
        テスト区分: UT
        テストカテゴリ: C0
        テスト区分: 正常系
        テストシナリオ: create_pre_processorメソッドがKanrenWithPreProcessorインスタンスを返し、PreProcessorを継承していることを確認
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        result = kanren_processor_factory.create_pre_processor()
        assert isinstance(result, KanrenWithPreProcessor), f"Expected KanrenWithPreProcessor, got {type(result)}"
        assert isinstance(result, PreProcessor), "KanrenWithPreProcessor does not inherit from PreProcessor"
        assert hasattr(result, 'chain_pre_process'), "KanrenWithPreProcessor does not have 'chain_pre_process' method"
        assert isinstance(result.chain_pre_process(), list), "chain_pre_process method should return a list"

    def test_create_post_processor_C0_returns_kanren_post_processor(self, kanren_processor_factory):
        test_doc = """
        テスト区分: UT
        テストカテゴリ: C0
        テスト区分: 正常系
        テストシナリオ: create_post_processorメソッドがKanrenWithPostProcessorインスタンスを返し、PostProcessorを継承していることを確認
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        result = kanren_processor_factory.create_post_processor()
        assert isinstance(result, KanrenWithPostProcessor), f"Expected KanrenWithPostProcessor, got {type(result)}"
        assert isinstance(result, PostProcessor), "KanrenWithPostProcessor does not inherit from PostProcessor"
        assert hasattr(result, 'chain_post_process'), "KanrenWithPostProcessor does not have 'chain_post_process' method"
        assert isinstance(result.chain_post_process(), list), "chain_post_process method should return a list"

class TestKanrenWithoutProcessorFactory:
    """KanrenProcessorFactoryクラスのテスト

    テスト構造:
    ├── C0: 基本機能テスト
    │   ├── create_pre_processor メソッドが KanrenWithoutPreProcessor インスタンスを返し、PreProcessor を継承していることを確認
    │   └── create_post_processor メソッドが KanrenWithoutPostProcessor インスタンスを返し、PostProcessor を継承していることを確認

    # C1のディシジョンテーブル
    C1テストは適用されないため、ディシジョンテーブルはありません。

    境界値検証ケース一覧:g
    このクラスには境界値テストを適用する数値パラメータや範囲を持つ入力がないため、
    境界値検証ケースはありません。
    """

    def setup_method(self):
        log_msg("test start", LogLevel.INFO)

    def teardown_method(self):
        log_msg(f"test end\n{'-'*80}\n", LogLevel.INFO)

    @pytest.fixture()
    def kanren_processor_factory(self):
        return KanrenWithoutProcessorFactory()

    def test_create_pre_processor_C0_returns_kanren_pre_processor(self, kanren_processor_factory):
        test_doc = """
        テスト区分: UT
        テストカテゴリ: C0
        テスト区分: 正常系
        テストシナリオ: create_pre_processorメソッドがKanrenWithPreProcessorインスタンスを返し、PreProcessorを継承していることを確認
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        result = kanren_processor_factory.create_pre_processor()
        assert isinstance(result, KanrenWithoutPreProcessor), f"Expected KanrenWithoutPreProcessor, got {type(result)}"
        assert isinstance(result, PreProcessor), "KanrenWithoutPreProcessor does not inherit from PreProcessor"
        assert hasattr(result, 'chain_pre_process'), "KanrenWithoutPreProcessor does not have 'chain_pre_process' method"
        assert isinstance(result.chain_pre_process(), list), "chain_pre_process method should return a list"

    def test_create_post_processor_C0_returns_kanren_post_processor(self, kanren_processor_factory):
        test_doc = """
        テスト区分: UT
        テストカテゴリ: C0
        テスト区分: 正常系
        テストシナリオ: create_post_processorメソッドがKanrenWithPostProcessorインスタンスを返し、PostProcessorを継承していることを確認
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        result = kanren_processor_factory.create_post_processor()
        assert isinstance(result, KanrenWithoutPostProcessor), f"Expected KanrenWithoutPostProcessor, got {type(result)}"
        assert isinstance(result, PostProcessor), "KanrenWithoutPostProcessor does not inherit from PostProcessor"
        assert hasattr(result, 'chain_post_process'), "KanrenWithoutPostProcessor does not have 'chain_post_process' method"
        assert isinstance(result.chain_post_process(), list), "chain_post_process method should return a list"
