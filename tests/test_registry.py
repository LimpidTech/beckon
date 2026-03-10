import pytest

from zope.interface import Interface

import beckon
from beckon import register, Collection, BeckonInterface
from beckon.registry import clear
from beckon.django import IModel

from .models import FakeArticle
from .serializers import FakeArticleSerializer


class _ISerializer(Interface):
    pass

ISerializer: BeckonInterface[type] = BeckonInterface(_ISerializer, infer_from='model')


@pytest.fixture(autouse=True)
def clean_registry():
    clear()
    yield
    clear()


class TestCallableModule:
    def test_module_is_callable(self):
        register(IModel, FakeArticle)

        result = beckon(IModel, 'tests.fakearticle')
        assert result is FakeArticle

    def test_module_exposes_register(self):
        assert beckon.register is register

    def test_module_exposes_beckon(self):
        from beckon import beckon as beckon_fn
        assert beckon.beckon is beckon_fn

    def test_module_exposes_clear(self):
        from beckon.registry import clear as clear_fn
        assert beckon.clear is clear_fn

    def test_module_exposes_add_name_resolver(self):
        from beckon.registry import add_name_resolver as anr
        assert beckon.add_name_resolver is anr

    def test_module_exposes_beckon_interface(self):
        assert beckon.BeckonInterface is BeckonInterface

    def test_module_exposes_collection(self):
        assert beckon.Collection is Collection


class TestRegisterModel:
    def test_registers_model(self):
        register(IModel, FakeArticle)

        results = beckon(IModel)
        assert len(results) == 1

    def test_model_name_inferred_from_meta(self):
        register(IModel, FakeArticle)

        result = beckon(IModel, 'tests.fakearticle')
        assert result is FakeArticle

    def test_returns_none_for_unknown_name(self):
        assert beckon(IModel, 'nonexistent') is None


class TestRegisterSerializer:
    def test_registers_serializer(self):
        register(ISerializer, FakeArticleSerializer)

        results = beckon(ISerializer)
        assert len(results) == 1

    def test_serializer_name_inferred_from_meta_model(self):
        register(ISerializer, FakeArticleSerializer)

        result = beckon(ISerializer, 'tests.fakearticle')
        assert result is FakeArticleSerializer

    def test_serializer_linked_to_model_via_relationship(self):
        register(IModel, FakeArticle)
        register(ISerializer, FakeArticleSerializer)

        model = beckon(IModel, 'tests.fakearticle')
        serializer = beckon(ISerializer, 'tests.fakearticle')

        assert model is FakeArticle
        assert serializer is FakeArticleSerializer


class TestReverseRelationship:
    def test_reverse_adapter_registered_automatically(self):
        register(IModel, FakeArticle)
        register(ISerializer, FakeArticleSerializer)

        assert beckon(ISerializer, 'tests.fakearticle') is FakeArticleSerializer
        assert beckon(IModel, 'tests.fakearticle') is FakeArticle

    def test_explicit_reverse_relationship(self):
        register(IModel, FakeArticle)
        register(ISerializer, FakeArticleSerializer, model=FakeArticle)

        assert beckon(ISerializer, 'tests.fakearticle') is FakeArticleSerializer
        assert beckon(IModel, 'tests.fakearticle') is FakeArticle


class TestCustomInferFrom:
    def test_custom_infer_from_attribute(self):
        class _IValidator(Interface):
            pass

        IValidator = BeckonInterface(_IValidator, infer_from='model')

        class FakeValidator:
            class Meta:
                model = FakeArticle

        register(IModel, FakeArticle)
        register(IValidator, FakeValidator)

        assert beckon(IValidator, 'tests.fakearticle') is FakeValidator

    def test_no_infer_from_skips_inference(self):
        class _IPermission(Interface):
            pass

        IPermission = BeckonInterface(_IPermission)

        class IsAdmin:
            name = 'is_admin'
            class Meta:
                model = FakeArticle

        register(IModel, FakeArticle)
        register(IPermission, IsAdmin)

        assert beckon(IPermission, 'is_admin') is IsAdmin
        assert beckon(IPermission, 'tests.fakearticle') is None


class TestRegisterCollection:
    def test_registers_collection(self):
        class _ICollection(Interface):
            pass

        ICollection = BeckonInterface(_ICollection)

        class Latest(Collection):
            name = 'latest'

            def items(self, request):
                return []

        register(ICollection, Latest)

        results = beckon(ICollection)
        assert len(results) == 1

    def test_collection_name_from_attribute(self):
        class _ICollection(Interface):
            pass

        ICollection = BeckonInterface(_ICollection)

        class Latest(Collection):
            name = 'latest'

            def items(self, request):
                return []

        register(ICollection, Latest)
        assert beckon(ICollection, 'latest') is Latest

    def test_collection_name_falls_back_to_class_name(self):
        class _ICollection(Interface):
            pass

        ICollection = BeckonInterface(_ICollection)

        class Trending(Collection):
            def items(self, request):
                return []

        register(ICollection, Trending)
        assert beckon(ICollection, 'Trending') is Trending


class TestExplicitName:
    def test_explicit_name_overrides_inference(self):
        register(IModel, FakeArticle, name='custom_name')

        assert beckon(IModel, 'custom_name') is FakeArticle
        assert beckon(IModel, 'tests.fakearticle') is None


class TestExplicitRelationships:
    def test_explicit_model_relationship(self):
        register(IModel, FakeArticle)
        register(ISerializer, FakeArticleSerializer, model=FakeArticle)

        assert beckon(ISerializer, 'tests.fakearticle') is FakeArticleSerializer


class TestFetchAll:
    def test_all_for_interface(self):
        class _ICollection(Interface):
            pass

        ICollection = BeckonInterface(_ICollection)

        register(IModel, FakeArticle)

        class Latest(Collection):
            name = 'latest'

            def items(self, request):
                return []

        register(ICollection, Latest)

        assert len(beckon(IModel)) == 1
        assert len(beckon(ICollection)) == 1

    def test_different_interfaces_are_independent(self):
        register(IModel, FakeArticle)
        register(ISerializer, FakeArticleSerializer)

        assert len(beckon(IModel)) == 1
        assert len(beckon(ISerializer)) == 1


class TestCustomInterface:
    def test_user_defined_interface(self):
        class _IPermission(Interface):
            pass

        IPermission = BeckonInterface(_IPermission)

        class IsAdmin:
            name = 'is_admin'

        register(IPermission, IsAdmin)
        assert beckon(IPermission, 'is_admin') is IsAdmin

    def test_custom_interfaces_are_independent(self):
        class _IPermission(Interface):
            pass

        class _IValidator(Interface):
            pass

        IPermission = BeckonInterface(_IPermission)
        IValidator = BeckonInterface(_IValidator)

        class IsAdmin:
            name = 'is_admin'

        class EmailValidator:
            name = 'email'

        register(IPermission, IsAdmin)
        register(IValidator, EmailValidator)

        assert len(beckon(IPermission)) == 1
        assert len(beckon(IValidator)) == 1
        assert beckon(IPermission, 'is_admin') is IsAdmin
        assert beckon(IValidator, 'email') is EmailValidator
