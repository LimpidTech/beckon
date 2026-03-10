from __future__ import annotations

from typing import Generic, TypeVar

from zope.interface import Interface


T = TypeVar('T')


class BeckonInterface(Generic[T]):
    _interface: type[Interface]
    _infer_from: str | None

    def __init__(self, interface: type[Interface], infer_from: str | None = None) -> None:
        self._interface = interface
        self._infer_from = infer_from

    def __class_getitem__(cls, item: type) -> type[BeckonInterface]:
        return cls

    @property
    def interface(self) -> type[Interface]:
        return self._interface

    @property
    def infer_from(self) -> str | None:
        return self._infer_from
