# summon

Stop trying to make fetch happen.

A typed component registry backed by `zope.interface`. Register
components behind formal interfaces. Look them up without circular
imports. Relationships are inferred and bidirectional.

## Install

```
pip install summon
```

For Django integration:

```
pip install summon[django]
```

## Quick Start

```python
from zope.interface import Interface
from summon import register, SummonInterface

class _IService(Interface):
    pass

IService = SummonInterface(_IService)
```

```python
# register
register(IService, MyService, name='email')

# summon
import summon

summon(IService, 'email')  # -> MyService
summon(IService)           # -> [('email', MyService)]
```

The module itself is callable — `import summon; summon(...)` works
without importing the function separately.

## Django Integration

Add `summon.django` to `INSTALLED_APPS`:

```python
INSTALLED_APPS = [
    'summon.django',
    # ...
]
```

This registers a name resolver for Django models (`_meta.label_lower`)
and provides `IModel`:

```python
from summon import register
from summon.django import IModel

from .models import Post

register(IModel, Post)
```

```python
import summon
from summon.django import IModel

Post = summon(IModel, 'posts.post')
```

## Custom Interfaces with Relationships

```python
from zope.interface import Interface
from summon import SummonInterface, register

class _ISerializer(Interface):
    pass

ISerializer = SummonInterface(_ISerializer, infer_from='model')
```

Register a serializer and it automatically links to its model:

```python
register(IModel, Post)
register(ISerializer, PostSerializer)  # infers from Meta.model

summon(ISerializer, 'posts.post')  # -> PostSerializer
summon(IModel, 'posts.post')       # -> Post (reverse works too)
```

## Type Safety

Interfaces carry generic type information:

```python
IModel: SummonInterface[type[Model]] = SummonInterface(_IModel)
```

mypy infers return types automatically:

```python
summon(IModel, 'auth.user')  # mypy sees: type[Model] | None
```

Define your own typed interfaces and get the same inference:

```python
IPermission: SummonInterface[type[BasePermission]] = SummonInterface(_IPermission)
summon(IPermission, 'is_admin')  # mypy sees: type[BasePermission] | None
```

## License

BSD 2-Clause. See LICENSE.
