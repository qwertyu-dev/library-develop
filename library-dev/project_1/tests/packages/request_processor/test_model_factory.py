import sys
from typing import Type

import pytest
from pydantic import BaseModel

from src.lib.common_utils.ibr_decorator_config import initialize_config
from src.lib.common_utils.ibr_enums import LogLevel
from src.model.dataclass.request_processor_jinji_model import JinjiModel
from src.model.dataclass.request_processor_kanren_with_model import KanrenWithModel
from src.model.dataclass.request_processor_kanren_without_model import KanrenWithoutModel
from src.model.dataclass.request_processor_kokuki_model import KokukiModel
from src.packages.request_processor.model_factory import (
    JinjiModelFactory,
    KanrenWithModelFactory,
    KanrenWithoutModelFactory,
    KokukiModelFactory,
    ModelFactory,
)

config = initialize_config(sys.modules[__name__])
log_msg = config.log_message
log_msg(str(config), LogLevel.DEBUG)

class TestModelFactory:
    """ModelFactoryクラスとそのサブクラスのテスト

    テスト構造:
    ├── C0: 基本機能テスト
    │   ├── ModelFactory.create_model: NotImplementedErrorの発生確認
    │   ├── JinjiModelFactory.create_model: 正しいモデルの返却確認
    │   ├── KokukiModelFactory.create_model: 正しいモデルの返却確認
    │   └── KanrenWithModelFactory.create_model: 正しいモデルの返却確認
    │   └── KanrenWithoutModelFactory.create_model: 正しいモデルの返却確認
    └── C1: 分岐カバレッジ (該当なし)

    C1のディシジョンテーブル:
    該当なし(条件分岐がないため)

    境界値検証ケース一覧:
    該当なし(入力パラメータがないため)
    """

    def setup_method(self):
        log_msg("test start", LogLevel.INFO)

    def teardown_method(self):
        log_msg(f"test end\n{'-'*80}\n", LogLevel.INFO)

    def test_model_factory_create_model_C0(self):
        test_doc = """
        テスト区分: UT
        テストカテゴリ: C0
        テストシナリオ: ModelFactoryのcreate_modelメソッドを呼び出す
        期待結果: NotImplementedErrorが発生すること
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        factory = ModelFactory()
        with pytest.raises(NotImplementedError):
            factory.create_model()

    @pytest.mark.parametrize(("factory_class", "expected_model"), [
        (JinjiModelFactory, JinjiModel),
        (KokukiModelFactory, KokukiModel),
        (KanrenWithModelFactory, KanrenWithModel),
        (KanrenWithoutModelFactory, KanrenWithoutModel),
    ])
    def test_concrete_factory_create_model_C0(self, factory_class, expected_model):
        test_doc = f"""
        テスト区分: UT
        テストカテゴリ: C0
        テストシナリオ: {factory_class.__name__}のcreate_modelメソッドを呼び出す
        期待結果: {expected_model.__name__}が返されること
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        factory = factory_class()
        model = factory.create_model()
        assert model == expected_model
        assert issubclass(model, BaseModel)
        log_msg(f"Returned model: {model}", LogLevel.DEBUG)

    def test_model_factory_create_model_existence_C0(self):
        test_doc = """
        テスト区分: UT
        テストケース: C0
        テストシナリオ: ModelFactoryクラスにcreate_modelメソッドが存在することを確認
        期待結果: create_modelメソッドが存在し、呼び出し可能であること
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        assert hasattr(ModelFactory, 'create_model')
        assert callable(ModelFactory.create_model)

    def test_model_factory_create_model_not_implemented_C0(self):
        test_doc = """
        テスト区分: UT
        テストケース: C0
        テストシナリオ: ModelFactoryのcreate_modelメソッドを呼び出す
        期待結果: NotImplementedErrorが発生すること
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        factory = ModelFactory()
        with pytest.raises(NotImplementedError):
            factory.create_model()

class TestJinjiModelFactory:
    """JinjiModelFactoryクラスのテスト

    テスト構造:
    ├── C0: 基本機能テスト
    │   └── create_model: JinjiModelを返すことの確認
    ├── C1: 分岐カバレッジ
    │   └── 該当なし(分岐がないため)
    ├── C2: 条件カバレッジ
    │   └── 該当なし(条件分岐がないため)
    └── BVT: 境界値テスト
        └── 該当なし(入力パラメータがないため)

    C1のディシジョンテーブル:
    該当なし(条件分岐がないため)

    境界値検証ケース一覧:
    該当なし(入力パラメータがないため)
    """

    def setup_method(self):
        log_msg("test start", LogLevel.INFO)

    def teardown_method(self):
        log_msg(f"test end\n{'-'*80}\n", LogLevel.INFO)

    def test_create_model_C0_returns_jinji_model(self):
        """JinjiModelFactoryのcreate_modelメソッドのテスト"""
        test_doc = """
        テスト区分: UT
        テストカテゴリ: C0
        テストシナリオ: create_modelメソッドがJinjiModelを返すことを確認
        期待結果: JinjiModelクラスが返される
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        factory = JinjiModelFactory()
        model = factory.create_model()

        assert model == JinjiModel
        assert issubclass(model, BaseModel)

        log_msg(f"Returned model: {model}", LogLevel.DEBUG)

    def test_create_model_C0_instance_check(self):
        """JinjiModelFactoryのcreate_modelメソッドの戻り値型チェック"""
        test_doc = """
        テスト区分: UT
        テストカテゴリ: C0
        テストシナリオ: create_modelメソッドの戻り値が適切な型であることを確認
        期待結果: 戻り値がType[BaseModel]のインスタンスである
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        factory = JinjiModelFactory()
        model = factory.create_model()

        assert isinstance(model, type)
        assert issubclass(model, BaseModel)

        log_msg(f"Model type: {type(model)}", LogLevel.DEBUG)

class TestKokukiModelFactory:
    """KokukiModelFactoryクラスのテスト

    テスト構造:
    ├── C0: 基本機能テスト
    │   └── create_model: KokukiModelを返すことの確認
    ├── C1: 分岐カバレッジ
    │   └── 該当なし(分岐がないため)
    ├── C2: 条件カバレッジ
    │   └── 該当なし(条件分岐がないため)
    └── BVT: 境界値テスト
        └── 該当なし(入力パラメータがないため)

    C1のディシジョンテーブル:
    該当なし(条件分岐がないため)

    境界値検証ケース一覧:
    該当なし(入力パラメータがないため)
    """

    def setup_method(self):
        log_msg("test start", LogLevel.INFO)

    def teardown_method(self):
        log_msg(f"test end\n{'-'*80}\n", LogLevel.INFO)

    def test_create_model_C0_returns_kokuki_model(self):
        """KokukiModelFactoryのcreate_modelメソッドのテスト"""
        test_doc = """
        テスト区分: UT
        テストカテゴリ: C0
        テストシナリオ: create_modelメソッドがKokukiModelを返すことを確認
        期待結果: KokukiModelクラスが返される
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        factory = KokukiModelFactory()
        model = factory.create_model()

        assert model == KokukiModel
        assert issubclass(model, BaseModel)

        log_msg(f"Returned model: {model}", LogLevel.DEBUG)

    def test_create_model_C0_instance_check(self):
        """KokukiModelFactoryのcreate_modelメソッドの戻り値型チェック"""
        test_doc = """
        テスト区分: UT
        テストカテゴリ: C0
        テストシナリオ: create_modelメソッドの戻り値が適切な型であることを確認
        期待結果: 戻り値がType[BaseModel]のインスタンスである
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        factory = KokukiModelFactory()
        model = factory.create_model()

        assert isinstance(model, type)
        assert issubclass(model, BaseModel)

        log_msg(f"Model type: {type(model)}", LogLevel.DEBUG)

class TestKanrenWithModelFactory:
    """KanrenWithModelFactoryクラスのテスト

    テスト構造:
    ├── C0: 基本機能テスト
    │   └── create_model: KanrenWithModelを返すことの確認
    ├── C1: 分岐カバレッジ
    │   └── 該当なし(分岐がないため)
    ├── C2: 条件カバレッジ
    │   └── 該当なし(条件分岐がないため)
    └── BVT: 境界値テスト
        └── 該当なし(入力パラメータがないため)

    C1のディシジョンテーブル:
    該当なし(条件分岐がないため)

    境界値検証ケース一覧:
    該当なし(入力パラメータがないため)
    """

    def setup_method(self):
        log_msg("test start", LogLevel.INFO)

    def teardown_method(self):
        log_msg(f"test end\n{'-'*80}\n", LogLevel.INFO)

    def test_create_model_C0_returns_kanren_model(self):
        """KanrenWithModelFactoryのcreate_modelメソッドのテスト"""
        test_doc = """
        テスト区分: UT
        テストカテゴリ: C0
        テストシナリオ: create_modelメソッドがKanrenWithModelを返すことを確認
        期待結果: KanrenWithModelクラスが返される
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        factory = KanrenWithModelFactory()
        model = factory.create_model()

        assert model == KanrenWithModel
        assert issubclass(model, BaseModel)

        log_msg(f"Returned model: {model}", LogLevel.DEBUG)

    def test_create_model_C0_instance_check(self):
        """KanrenWithModelFactoryのcreate_modelメソッドの戻り値型チェック"""
        test_doc = """
        テスト区分: UT
        テストカテゴリ: C0
        テストシナリオ: create_modelメソッドの戻り値が適切な型であることを確認
        期待結果: 戻り値がType[BaseModel]のインスタンスである
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        factory = KanrenWithModelFactory()
        model = factory.create_model()

        assert isinstance(model, type)
        assert issubclass(model, BaseModel)

        log_msg(f"Model type: {type(model)}", LogLevel.DEBUG)

class TestKanrenWithoutModelFactory:
    """KanrenWithModelFactoryクラスのテスト

    テスト構造:
    ├── C0: 基本機能テスト
    │   └── create_model: KanrenWithoutModelを返すことの確認
    ├── C1: 分岐カバレッジ
    │   └── 該当なし(分岐がないため)
    ├── C2: 条件カバレッジ
    │   └── 該当なし(条件分岐がないため)
    └── BVT: 境界値テスト
        └── 該当なし(入力パラメータがないため)

    C1のディシジョンテーブル:
    該当なし(条件分岐がないため)

    境界値検証ケース一覧:
    該当なし(入力パラメータがないため)
    """

    def setup_method(self):
        log_msg("test start", LogLevel.INFO)

    def teardown_method(self):
        log_msg(f"test end\n{'-'*80}\n", LogLevel.INFO)

    def test_create_model_C0_returns_kanren_model(self):
        """KanrenWithModelFactoryのcreate_modelメソッドのテスト"""
        test_doc = """
        テスト区分: UT
        テストカテゴリ: C0
        テストシナリオ: create_modelメソッドがKanrenWithModelを返すことを確認
        期待結果: KanrenWithModelクラスが返される
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        factory = KanrenWithoutModelFactory()
        model = factory.create_model()

        assert model == KanrenWithoutModel
        assert issubclass(model, BaseModel)

        log_msg(f"Returned model: {model}", LogLevel.DEBUG)

    def test_create_model_C0_instance_check(self):
        """KanrenWithModelFactoryのcreate_modelメソッドの戻り値型チェック"""
        test_doc = """
        テスト区分: UT
        テストカテゴリ: C0
        テストシナリオ: create_modelメソッドの戻り値が適切な型であることを確認
        期待結果: 戻り値がType[BaseModel]のインスタンスである
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        factory = KanrenWithoutModelFactory()
        model = factory.create_model()

        assert isinstance(model, type)
        assert issubclass(model, BaseModel)

        log_msg(f"Model type: {type(model)}", LogLevel.DEBUG)
