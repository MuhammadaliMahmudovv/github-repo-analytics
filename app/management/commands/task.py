from django.core.management.base import BaseCommand

from app.models import Language, LanguageRepo, Topic, TopicRepo, Repo, RepoOwner
from django.db import transaction
from django.db import connection
import time
import gc
import orjson

REPO_COLUMNS = (
    "id, owner_id, name, stars, forks, watchers, is_fork, is_archived, "
    "topics_count, disk_usage, pull_requests, issues, description, "
    "primary_language_id, created_at, pushed_at, default_branch_commit, "
    "license, assignable_user_count, code_of_conduct, forking_allowed, "
    "parent_name_with_owner"
)


def copy_rows(cursor, table, columns, rows):
    with cursor.copy(f"COPY {table} ({columns}) FROM STDIN") as copy:
        for row in rows:
            copy.write_row(row)


class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        gc.disable()
        try:
            start = time.perf_counter()
            read_json = time.perf_counter()
            with open("part1.json", "rb") as f:
                data = orjson.loads(f.read())
            end_json = time.perf_counter()
            latest = {}
            for1 = time.perf_counter()
            for item in data:
                key = (item["owner"], item["name"])
                old = latest.get(key)
                if old is None or (item["stars"] or 0) > (old["stars"] or 0):
                    latest[key] = item
            end_for1 = time.perf_counter()
            data = list(latest.values())
            owner_ids = {}
            language_ids = {}
            topic_ids = {}
            topic_stars = {}

            repo_rows = []
            language_repo_rows = []
            topic_repo_rows = []
            for2 = time.perf_counter()
            for repo_id, item in enumerate(data, 1):
                owner_id = owner_ids.setdefault(item["owner"], len(owner_ids) + 1)
                primary = item["primaryLanguage"]
                primary_id = (
                    language_ids.setdefault(primary, len(language_ids) + 1)
                    if primary
                    else None
                )
                parent = item["parent"]
                if isinstance(parent, dict):
                    parent = parent.get("nameWithOwner")

                repo_rows.append(
                    (
                        repo_id,
                        owner_id,
                        item["name"],
                        item["stars"],
                        item["forks"],
                        item["watchers"],
                        item["isFork"],
                        item["isArchived"],
                        item["topicCount"],
                        item["diskUsageKb"],
                        item["pullRequests"],
                        item["issues"],
                        item["description"],
                        primary_id,
                        item["createdAt"],
                        item["pushedAt"],
                        item["defaultBranchCommitCount"],
                        item["license"],
                        item["assignableUserCount"],
                        item["codeOfConduct"],
                        item["forkingAllowed"],
                        parent,
                    )
                )
                for3 = time.perf_counter()
                for lang in item["languages"]:
                    lang_id = language_ids.setdefault(
                        lang["name"], len(language_ids) + 1
                    )
                    language_repo_rows.append((lang_id, repo_id, lang["size"]))
                end_for3 = time.perf_counter()
                for4 = time.perf_counter()
                for topic in item["topics"]:
                    topic_id = topic_ids.setdefault(topic["name"], len(topic_ids) + 1)
                    topic_stars[topic_id] = topic["stars"]
                    topic_repo_rows.append((topic_id, repo_id))
                end_for4 = time.perf_counter()
            end_for2 = time.perf_counter()
            owner_rows = [(i, name) for name, i in owner_ids.items()]
            language_rows = [(i, name) for name, i in language_ids.items()]
            topic_rows = [(i, name, topic_stars[i]) for name, i in topic_ids.items()]

            with transaction.atomic():
                with connection.cursor() as c:
                    cursor = c.cursor
                    cursor.execute(
                        "TRUNCATE app_repoowner, app_language, app_topic, app_repo, "
                        "app_languagerepo, app_topicrepo RESTART IDENTITY"
                    )
                    copy_rows(cursor, "app_repoowner", "id, name", owner_rows)
                    copy_rows(cursor, "app_language", "id, name", language_rows)
                    copy_rows(cursor, "app_topic", "id, name, stars", topic_rows)
                    copy_rows(cursor, "app_repo", REPO_COLUMNS, repo_rows)
                    copy_rows(
                        cursor,
                        "app_languagerepo",
                        "language_id, repo_id, size",
                        language_repo_rows,
                    )
                    copy_rows(
                        cursor, "app_topicrepo", "topic_id, repo_id", topic_repo_rows
                    )
            end = time.perf_counter()

            print(f"total time: {end - start:.2f} sec.")
            print(f"reading json: {end_json - read_json:.2f} sec.")
            print(f"for1: {end_for1 - for1:.2f} sec.")
            print(f"for2: {end_for2 - for2:.2f} sec.")
            print(f"for3: {end_for3 - for3:.2f} sec.")
            print(f"for4: {end_for4 - for4:.2f} sec.")
        finally:
            gc.enable()
