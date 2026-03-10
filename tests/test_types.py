"""Type checking test file — run with mypy, not pytest."""

from django.db import models
from rest_framework.serializers import Serializer

from zope.interface import Interface

from beckon import BeckonInterface, beckon
from beckon.django import IModel


# Built-in interface
def test_beckon_model() -> None:
    result = beckon(IModel, 'auth.user')
    reveal_type(result)

def test_beckon_all_models() -> None:
    result = beckon(IModel)
    reveal_type(result)


# Custom interface with relationship
class _ISerializer(Interface):
    pass

ISerializer: BeckonInterface[type[Serializer]] = BeckonInterface(_ISerializer, infer_from='model')

def test_beckon_serializer_via_relation() -> None:
    result = beckon(ISerializer, 'posts.post')
    reveal_type(result)

def test_beckon_model_via_reverse_relation() -> None:
    result = beckon(IModel, 'posts.post')
    reveal_type(result)


# Custom user-defined interface
class BasePermission:
    pass

class _IPermission(Interface):
    pass

IPermission: BeckonInterface[type[BasePermission]] = BeckonInterface(_IPermission)

def test_beckon_custom() -> None:
    result = beckon(IPermission, 'is_admin')
    reveal_type(result)

def test_beckon_all_custom() -> None:
    result = beckon(IPermission)
    reveal_type(result)
