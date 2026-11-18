from django.db.models import Count
from django.db.models.functions import ExtractYear
from rest_framework.response import Response
from django.db.models.functions import ExtractYear
from rest_framework.views import APIView

from app.models import Language


class LanguageStatsView(APIView):
    def get(self, request): ...
