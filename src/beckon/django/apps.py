from django.apps import AppConfig, apps

from acq.django import discover

from beckon import register

from . import IModel


class BeckonConfig(AppConfig):
    name = 'beckon.django'

    def ready(self):
        for model in apps.get_models():
            register(IModel, model)

        discover('resources')
