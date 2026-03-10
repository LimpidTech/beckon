import pytest

from zope.interface import Interface

import summon
from summon import register, Collection, SummonInterface
from summon.registry import clear
from summon.django import IModel

from .models import FakeArticle
from .serializers import FakeArticleSerializer


class _ISerializer(Interface):
    pass

ISerializer: SummonInterface[type] = SummonInterface(_ISerializer, infer_from='model')


@pytest.fixture(autouse=True)
def clean_registry():
    clear()
    yield
    clear()


class TestCallableModule:
    def test_module_is_callable(self):
        register(IModel, FakeArticle)

        result = summon(IModel, 'tests.fakearticle')
        assert result is FakeArticle


class TestRegisterModel:
    def test_registers_model(self):
        register(IModel, FakeArticle)

        results = summon(IModel)
        assert len(results) == 1

    def test_model_name_inferred_from_meta(self):
        register(IModel, FakeArticle)

        result = summon(IModel, 'tests.fakearticle')
        assert result is FakeArticle

    def test_returns_none_for_unknown_name(self):
        assert summon(IModel, 'nonexistent') is None


class TestRegisterSerializer:
    def test_registers_serializer(self):
        register(ISerializer, FakeArticleSerializer)

        results = summon(ISerializer)
        assert len(results) == 1

    def test_serializer_name_inferred_from_meta_model(self):
        register(ISerializer, FakeArticleSerializer)

        result = summon(ISerializer, 'tests.fakearticle')
        assert result is FakeArticleSerializer

    def test_serializer_linked_to_model_via_relationship(self):
        register(IModel, FakeArticle)
        register(ISerializer, FakeArticleSerializer)

        model = summon(IModel, 'tests.fakearticle')
        serializer = summon(ISerializer, 'tests.fakearticle')

        assert model is FakeArticle
        assert serializer is FakeArticleSerializer


class TestReverseRelationship:
    def test_reverse_adapter_registered_automatically(self):
        register(IModel, FakeArticle)
        register(ISerializer, FakeArticleSerializer)

        assert summon(ISerializer, 'tests.fakearticle') is FakeArticleSerializer
        assert summon(IModel, 'tests.fakearticle') is FakeArticle

    def test_explicit_reverse_relationship(self):
        register(IModel, FakeArticle)
        register(ISerializer, FakeArticleSerializer, model=FakeArticle)

        assert summon(ISerializer, 'tests.fakearticle') is FakeArticleSerializer
        assert summon(IModel, 'tests.fakearticle') is FakeArticle


class TestCustomInferFrom:
    def test_custom_infer_from_attribute(self):
        class _IValidator(Interface):
            pass

        IValidator = SummonInterface(_IValidator, infer_from='model')

        class FakeValidator:
            class Meta:
                model = FakeArticle

        register(IModel, FakeArticle)
        register(IValidator, FakeValidator)

        assert summon(IValidator, 'tests.fakearticle') is FakeValidator

    def test_no_infer_from_skips_inference(self):
        class _IPermission(Interface):
            pass

        IPermission = SummonInterface(_IPermission)

        class IsAdmin:
            name = 'is_admin'
            class Meta:
                model = FakeArticle

        register(IModel, FakeArticle)
        register(IPermission, IsAdmin)

        assert summon(IPermission, 'is_admin') is IsAdmin
        assert summon(IPermission, 'tests.fakearticle') is None


class TestRegisterCollection:
    def test_registers_collection(self):
        class _ICollection(Interface):
            pass

        ICollection = SummonInterface(_ICollection)

        class Latest(Collection):
            name = 'latest'

            def items(self, request):
                return []

        register(ICollection, Latest)

        results = summon(ICollection)
        assert len(results) == 1

    def test_collection_name_from_attribute(self):
        class _ICollection(Interface):
            pass

        ICollection = SummonInterface(_ICollection)

        class Latest(Collection):
            name = 'latest'

            def items(self, request):
                return []

        register(ICollection, Latest)
        assert summon(ICollection, 'latest') is Latest

    def test_collection_name_falls_back_to_class_name(self):
        class _ICollection(Interface):
            pass

        ICollection = SummonInterface(_ICollection)

        class Trending(Collection):
            def items(self, request):
                return []

        register(ICollection, Trending)
        assert summon(ICollection, 'Trending') is Trending


class TestExplicitName:
    def test_explicit_name_overrides_inference(self):
        register(IModel, FakeArticle, name='custom_name')

        assert summon(IModel, 'custom_name') is FakeArticle
        assert summon(IModel, 'tests.fakearticle') is None


class TestExplicitRelationships:
    def test_explicit_model_relationship(self):
        register(IModel, FakeArticle)
        register(ISerializer, FakeArticleSerializer, model=FakeArticle)

        assert summon(ISerializer, 'tests.fakearticle') is FakeArticleSerializer


class TestFetchAll:
    def test_all_for_interface(self):
        class _ICollection(Interface):
            pass

        ICollection = SummonInterface(_ICollection)

        register(IModel, FakeArticle)

        class Latest(Collection):
            name = 'latest'

            def items(self, request):
                return []

        register(ICollection, Latest)

        assert len(summon(IModel)) == 1
        assert len(summon(ICollection)) == 1

    def test_different_interfaces_are_independent(self):
        register(IModel, FakeArticle)
        register(ISerializer, FakeArticleSerializer)

        assert len(summon(IModel)) == 1
        assert len(summon(ISerializer)) == 1


class TestCustomInterface:
    def test_user_defined_interface(self):
        class _IPermission(Interface):
            pass

        IPermission = SummonInterface(_IPermission)

        class IsAdmin:
            name = 'is_admin'

        register(IPermission, IsAdmin)
        assert summon(IPermission, 'is_admin') is IsAdmin

    def test_custom_interfaces_are_independent(self):
        class _IPermission(Interface):
            pass

        class _IValidator(Interface):
            pass

        IPermission = SummonInterface(_IPermission)
        IValidator = SummonInterface(_IValidator)

        class IsAdmin:
            name = 'is_admin'

        class EmailValidator:
            name = 'email'

        register(IPermission, IsAdmin)
        register(IValidator, EmailValidator)

        assert len(summon(IPermission)) == 1
        assert len(summon(IValidator)) == 1
        assert summon(IPermission, 'is_admin') is IsAdmin
        assert summon(IValidator, 'email') is EmailValidator
