from typing import Any, Callable, TypeVar, overload

from .collection import Collection as Collection
from .interfaces import SummonInterface as SummonInterface
from .registry import add_name_resolver as add_name_resolver
from .registry import clear as clear
from .registry import register as register
from .registry import summon as summon

T = TypeVar('T')

@overload
def __call__(interface: SummonInterface[T], name: str) -> T | None: ...
@overload
def __call__(interface: SummonInterface[T]) -> list[tuple[str, T]]: ...
