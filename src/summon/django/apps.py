from django.apps import AppConfig

from acq.django import discover


class SummonConfig(AppConfig):
    name = 'summon.django'

    def ready(self):
        discover('resources')
