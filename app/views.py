from django.db.models.functions import ExtractYear, RowNumber
from django.db.models import Count, F, Window
from rest_framework.response import Response
from rest_framework.views import APIView
from collections import defaultdict
from django.db.models import Count
from .models import Repo


class StatisticsView(APIView):
    def get(self, request):
        rows = (
            Repo.objects.annotate(year=ExtractYear("created_at"))
            .values("year", "languages__name")
            .annotate(count=Count("id"))
            .annotate(
                rn=Window(
                    RowNumber(),
                    partition_by=F("year"),
                    order_by=[F("count").desc(), "languages__name"],
                )
            )
            .filter(rn__lte=5)
        )

        by_year = defaultdict(list)
        for row in rows:
            langs = by_year[row["year"]]
            if len(langs) < 5:
                langs.append(
                    {"language": row["languages__name"], "count": row["count"]}
                )

        return Response(
            [{"year": y, "languages": langs} for y, langs in by_year.items()]
        )
