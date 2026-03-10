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

Define an interface:

```python
from zope.interface import Interface
from beckon import BeckonInterface

class _IService(Interface):
    pass

IService = BeckonInterface(_IService)
```

Register components and look them up:

```python
from beckon import register

register(IService, MyService, name='email')
```

```python
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

This does three things:

1. Registers every Django model with `IModel` automatically
2. Registers a name resolver so models are named by
   `_meta.label_lower` (e.g. `posts.post`)
3. Auto-discovers `resources.py` in every installed app via
   [acq](https://pypi.org/project/acq/)

Every model is available immediately:

```python
import beckon
from beckon.django import IModel

Post = beckon(IModel, 'posts.post')
```

For anything beyond models (serializers, permissions, custom
interfaces), put `register()` calls in a `resources.py` file
inside any installed app. beckon finds them automatically on
startup:

```python
# posts/resources.py

from beckon import register
from myapp.interfaces import ISerializer

from .serializers import PostSerializer

register(ISerializer, PostSerializer)  # infers model from Meta.model
```

## Custom Interfaces with Relationships

```python
from zope.interface import Interface
from beckon import BeckonInterface

class _ISerializer(Interface):
    pass

ISerializer = BeckonInterface(_ISerializer, infer_from='model')
```

The `infer_from` parameter tells beckon which attribute to check
when inferring relationships. When a component has a `Meta.model`
attribute pointing to a registered model, beckon links them
automatically:

```python
# posts/resources.py

from beckon import register
from myapp.interfaces import ISerializer

from .serializers import PostSerializer

register(ISerializer, PostSerializer)  # infers model from Meta.model
```

Since models are already registered, beckon links the serializer
to its model automatically:

```python
import beckon

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
