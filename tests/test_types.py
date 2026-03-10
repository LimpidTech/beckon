"""Type checking test file — run with mypy, not pytest."""

from django.db import models
from rest_framework.serializers import Serializer

from zope.interface import Interface

from summon import SummonInterface, summon
from summon.django import IModel


# Built-in interface
def test_summon_model() -> None:
    result = summon(IModel, 'auth.user')
    reveal_type(result)

def test_summon_all_models() -> None:
    result = summon(IModel)
    reveal_type(result)


# Custom interface with relationship
class _ISerializer(Interface):
    pass

ISerializer: SummonInterface[type[Serializer]] = SummonInterface(_ISerializer, infer_from='model')

def test_summon_serializer_via_relation() -> None:
    result = summon(ISerializer, 'posts.post')
    reveal_type(result)

def test_summon_model_via_reverse_relation() -> None:
    result = summon(IModel, 'posts.post')
    reveal_type(result)


# Custom user-defined interface
class BasePermission:
    pass

class _IPermission(Interface):
    pass

IPermission: SummonInterface[type[BasePermission]] = SummonInterface(_IPermission)

def test_summon_custom() -> None:
    result = summon(IPermission, 'is_admin')
    reveal_type(result)

def test_summon_all_custom() -> None:
    result = summon(IPermission)
    reveal_type(result)
