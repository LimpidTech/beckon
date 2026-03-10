from __future__ import annotations

from typing import Generic, TypeVar

from zope.interface import Interface


T = TypeVar('T')


class SummonInterface(Generic[T]):
    """A typed interface for the summon registry.

    Wraps a zope.interface.Interface and carries type information
    so that mypy can infer return types from summon() calls.

    Define typed interfaces:

        IModel = SummonInterface[type[Model]]
        ISerializer = SummonInterface[type[Serializer]], infer_from='model')

    The `infer_from` parameter tells the registry which attribute
    to check when inferring relationships. Attribute resolution can
    be customized by providing name_resolvers to the registry.

    """

    _interface: type[Interface]
    _infer_from: str | None

    def __init__(self, interface: type[Interface], infer_from: str | None = None) -> None:
        self._interface = interface
        self._infer_from = infer_from

    def __class_getitem__(cls, item: type) -> type[SummonInterface]:
        return cls

    @property
    def interface(self) -> type[Interface]:
        return self._interface

    @property
    def infer_from(self) -> str | None:
        return self._infer_from
