from django.apps import AppConfig

from acq.django import discover


class BeckonConfig(AppConfig):
    name = 'beckon.django'

    def ready(self):
        discover('resources')
