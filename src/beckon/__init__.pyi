from typing import Any, Callable, TypeVar, overload

from .collection import Collection as Collection
from .interfaces import BeckonInterface as BeckonInterface
from .registry import add_name_resolver as add_name_resolver
from .registry import clear as clear
from .registry import register as register
from .registry import beckon as beckon

T = TypeVar('T')

@overload
def __call__(interface: BeckonInterface[T], name: str) -> T | None: ...
@overload
def __call__(interface: BeckonInterface[T]) -> list[tuple[str, T]]: ...
