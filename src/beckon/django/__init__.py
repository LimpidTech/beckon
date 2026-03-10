from __future__ import annotations

from typing import Any, TYPE_CHECKING

from zope.interface import Interface

from beckon import BeckonInterface, add_name_resolver

if TYPE_CHECKING:
    from django.db.models import Model


def _django_name_resolver(component: Any) -> str | None:
    """Resolve names from Django's _meta.label_lower and Meta.model/queryset."""

    meta = getattr(component, '_meta', None)

    if meta is not None:
        label = getattr(meta, 'label_lower', None)

        if label is not None:
            return label

    inner_meta = getattr(component, 'Meta', None)

    if inner_meta is not None:
        model = getattr(inner_meta, 'model', None)

        if model is not None:
            return model._meta.label_lower

        queryset = getattr(inner_meta, 'queryset', None)

        if queryset is not None:
            return queryset.model._meta.label_lower

    return None


def _django_infer_from_resolver(component: Any, attr: str) -> Any | None:
    """Resolve Meta.queryset.model when looking up 'model'."""

    inner_meta = getattr(component, 'Meta', None)

    if inner_meta is None:
        return None

    if attr == 'model':
        queryset = getattr(inner_meta, 'queryset', None)

        if queryset is not None:
            return queryset.model

    return None


add_name_resolver(_django_name_resolver)


class _IModel(Interface):
    """A Django model."""


IModel: BeckonInterface[type[Model]] = BeckonInterface(_IModel)
