from django.db import models


class FakeArticle(models.Model):
    title = models.CharField(max_length=255)

    class Meta:
        app_label = 'tests'
