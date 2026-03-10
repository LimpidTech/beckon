from rest_framework import serializers

from .models import FakeArticle


class FakeArticleSerializer(serializers.ModelSerializer):
    class Meta:
        model = FakeArticle
        fields = ['id', 'title']
