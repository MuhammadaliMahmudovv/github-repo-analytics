from django.core.management.base import BaseCommand

from app.models import Language, LanguageRepo, Topic, TopicRepo, Repo, RepoOwner
from django.db import transaction
from django.db import connection
import time
import gc
import orjson


class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        with open("part1.json", "rb") as f:
            data = orjson.loads(f.read())
