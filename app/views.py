from rest_framework.response import Response
from rest_framework.views import APIView
from django.http import JsonResponse
from collections import defaultdict
from django.db.models import Count
from .models import Language, Repo


class StatisticsView(APIView):
    def get(self, request):
        result = []
        for date in Repo.objects.dates("created_at", "year"):
            top = (
                Language.objects.filter(repos__created_at__year=date.year)
                .annotate(repo_count=Count("repos"))
                .order_by("-repo_count", "name")[:5]
            )
            result.append(
                {
                    "year": date.year,
                    "languages": [
                        {"language": lang.name, "repos": lang.repo_count}
                        for lang in top
                    ],
                }
            )
        return Response(result)
