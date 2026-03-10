import sys
import types

from .registry import register, summon, add_name_resolver, clear
from .collection import Collection
from .interfaces import SummonInterface

__all__ = [
    'register',
    'summon',
    'add_name_resolver',
    'clear',
    'Collection',
    'SummonInterface',
]


class _SummonModule(types.ModuleType):
    register = staticmethod(register)
    summon = staticmethod(summon)
    add_name_resolver = staticmethod(add_name_resolver)
    clear = staticmethod(clear)
    Collection = Collection
    SummonInterface = SummonInterface

    def __call__(self, *args, **kwargs):
        return summon(*args, **kwargs)


sys.modules[__name__].__class__ = _SummonModule
