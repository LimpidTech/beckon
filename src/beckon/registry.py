from __future__ import annotations

from typing import Any, Callable, TypeVar, overload

from zope.interface.adapter import AdapterRegistry

from .interfaces import BeckonInterface


T = TypeVar('T')

_registry = AdapterRegistry()

_component_index: dict[int, tuple[BeckonInterface[Any], str]] = {}
_known_interfaces: list[BeckonInterface[Any]] = []
_name_resolvers: list[Callable[[Any], str | None]] = []


def _resolve_name(component: Any) -> str:
    # Explicit name attribute always wins
    name = getattr(component, 'name', None)

    if isinstance(name, str):
        return name

    # Framework-specific resolvers (e.g. Django _meta.label_lower)
    for resolver in _name_resolvers:
        name = resolver(component)

        if name is not None:
            return name

    name = getattr(component, '__name__', None)

    if name is not None:
        return name

    raise ValueError(f'Cannot infer name for {component!r}. Provide an explicit name.')


def _resolve_infer_from(component: Any, attr: str) -> Any | None:
    inner_meta = getattr(component, 'Meta', None)

    if inner_meta is not None:
        value = getattr(inner_meta, attr, None)

        if value is not None:
            return value

    return getattr(component, attr, None)


def _infer_adapts(interface: BeckonInterface[Any], component: Any) -> list[tuple[BeckonInterface[Any], str]]:
    results = []

    if interface.infer_from is not None:
        related = _resolve_infer_from(component, interface.infer_from)

        if related is not None:
            index_key = id(related)

            if index_key in _component_index:
                rel_interface, rel_name = _component_index[index_key]
                results.append((rel_interface, rel_name))

    return results


def _register_adapter(from_iface: BeckonInterface[Any], to_iface: BeckonInterface[Any], name: str, component: Any) -> None:
    _registry.register(
        [from_iface.interface], to_iface.interface, name, component,
    )

    from_component = _registry.lookup([], from_iface.interface, name)

    if from_component is not None:
        _registry.register(
            [to_iface.interface], from_iface.interface, name, from_component,
        )


def add_name_resolver(resolver: Callable[[Any], str | None]) -> None:
    """Add a name resolver to the registry.

    Resolvers run after the explicit `name` attribute check but before
    Meta.model and __name__ fallbacks. The first resolver to return a
    non-None string wins.

    """

    _name_resolvers.insert(0, resolver)


@overload
def beckon(interface: BeckonInterface[T], name: str) -> T | None: ...

@overload
def beckon(interface: BeckonInterface[T]) -> list[tuple[str, T]]: ...


def beckon(interface: BeckonInterface[T], name: str | None = None) -> T | list[tuple[str, T]] | None:
    """Look up registered components.

        beckon(IModel)                     # all
        beckon(IModel, 'posts.post')       # by name
        beckon(ISerializer, 'posts.post')  # via adapter

    Adapter lookups work in both directions.

    """

    zope_iface = interface.interface

    if name is not None:
        result = _registry.lookup([], zope_iface, name)

        if result is not None:
            return result

        for related_iface in _known_interfaces:
            if related_iface is interface:
                continue

            adapter = _registry.lookup([related_iface.interface], zope_iface, name)

            if adapter is not None:
                return adapter

        return None

    return _registry.lookupAll([], zope_iface)


def register(interface: BeckonInterface[Any], component: Any, name: str | None = None, **adapts: Any) -> None:
    """Register a component under an interface.

        register(IModel, Post)
        register(ISerializer, PostSerializer)

    Relationships are inferred from the interface's infer_from
    setting, or provided explicitly:

        register(ISerializer, PostSerializer, model=Post)

    Adapters are registered in both directions automatically.

    """

    zope_iface = interface.interface

    if name is None:
        name = _resolve_name(component)

    _registry.register([], zope_iface, name, component)
    _component_index[id(component)] = (interface, name)

    if interface not in _known_interfaces:
        _known_interfaces.append(interface)

    for rel_interface, rel_name in _infer_adapts(interface, component):
        _register_adapter(rel_interface, interface, name, component)

    for _, rel_component in adapts.items():
        index_key = id(rel_component)

        if index_key in _component_index:
            rel_interface, _ = _component_index[index_key]
            _register_adapter(rel_interface, interface, name, component)


def clear() -> None:
    """Clear the registry."""

    global _registry, _component_index, _known_interfaces
    _registry = AdapterRegistry()
    _component_index = {}
    _known_interfaces = []
