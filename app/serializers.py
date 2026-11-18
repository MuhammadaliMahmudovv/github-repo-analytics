from rest_framework import serializers
from .models import MyModel, Language, Topics


class LanguageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Language
        fields = ["name"]


class StatisticsSerializer(serializers.ModelSerializer):
    languages = LanguageSerializer(read_only=True, many=True)

    class Meta:
        model = MyModel
        fields = [
            "owner",
            "name",
            "stars",
            "forks",
            "watchers",
            "languages_count",
            "languages",
            "pushed_at",
        ]
