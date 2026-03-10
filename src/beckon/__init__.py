import sys
import types

from .registry import register, beckon, add_name_resolver, clear
from .collection import Collection
from .interfaces import BeckonInterface

__all__ = [
    'register',
    'beckon',
    'add_name_resolver',
    'clear',
    'Collection',
    'BeckonInterface',
]


class _BeckonModule(types.ModuleType):
    def __call__(self, *args, **kwargs):
        return beckon(*args, **kwargs)


sys.modules[__name__].__class__ = _BeckonModule
