# beckon

Stop trying to make fetch happen.

A typed component registry backed by `zope.interface`. Register
components behind formal interfaces. Look them up without circular
imports. Relationships are inferred and bidirectional.

## Install

```
pip install beckon
```

For Django integration:

```
pip install beckon[django]
```

## Quick Start

```python
from zope.interface import Interface
from beckon import register, BeckonInterface

class _IService(Interface):
    pass

IService = BeckonInterface(_IService)
```

```python
# register
register(IService, MyService, name='email')

# beckon
import beckon

beckon(IService, 'email')  # -> MyService
beckon(IService)           # -> [('email', MyService)]
```

The module itself is callable — `import beckon; beckon(...)` works
without importing the function separately.

## Django Integration

Add `beckon.django` to `INSTALLED_APPS`:

```python
INSTALLED_APPS = [
    'beckon.django',
    # ...
]
```

This registers a name resolver for Django models (`_meta.label_lower`)
and provides `IModel`:

```python
from beckon import register
from beckon.django import IModel

from .models import Post

register(IModel, Post)
```

```python
import beckon
from beckon.django import IModel

Post = beckon(IModel, 'posts.post')
```

## Custom Interfaces with Relationships

```python
from zope.interface import Interface
from beckon import BeckonInterface, register

class _ISerializer(Interface):
    pass

ISerializer = BeckonInterface(_ISerializer, infer_from='model')
```

Register a serializer and it automatically links to its model:

```python
register(IModel, Post)
register(ISerializer, PostSerializer)  # infers from Meta.model

beckon(ISerializer, 'posts.post')  # -> PostSerializer
beckon(IModel, 'posts.post')       # -> Post (reverse works too)
```

## Type Safety

Interfaces carry generic type information:

```python
IModel: BeckonInterface[type[Model]] = BeckonInterface(_IModel)
```

mypy infers return types automatically:

```python
beckon(IModel, 'auth.user')  # mypy sees: type[Model] | None
```

Define your own typed interfaces and get the same inference:

```python
IPermission: BeckonInterface[type[BasePermission]] = BeckonInterface(_IPermission)
beckon(IPermission, 'is_admin')  # mypy sees: type[BasePermission] | None
```

## License

BSD 2-Clause. See LICENSE.
