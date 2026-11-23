import gc
import time

import orjson
from django.core.management.base import BaseCommand
from django.db import connection, transaction

REPO_COLUMNS = (
    "id, owner_id, name, stars, forks, watchers, is_fork, is_archived, "
    "topics_count, disk_usage, pull_requests, issues, description, "
    "primary_language_id, created_at, pushed_at, default_branch_commit, "
    "license, assignable_user_count, code_of_conduct, forking_allowed, "
    "parent_name_with_owner"
)


def get_id(ids, name):
    if name not in ids:
        ids[name] = len(ids) + 1
    return ids[name]


class Command(BaseCommand):

    def handle(self, *args, **options):
        gc.disable()
        try:
            total = time.perf_counter()

            t = time.perf_counter()
            with open("part1.json", "rb") as f:
                data = orjson.loads(f.read())

            t = time.perf_counter()
            best = {}
            for repo in data:
                key = (repo["owner"], repo["name"])
                if key not in best or (repo["stars"] or 0) > (best[key]["stars"] or 0):
                    best[key] = repo
            repos = list(best.values())

            t = time.perf_counter()
            owners = {}
            languages = {}
            topics = {}
            topic_stars = {}

            repo_rows = []
            language_links = []
            topic_links = []

            for repo_id, repo in enumerate(repos, start=1):
                owner_id = get_id(owners, repo["owner"])

                primary_id = None
                if repo["primaryLanguage"]:
                    primary_id = get_id(languages, repo["primaryLanguage"])

                parent = repo["parent"]
                if isinstance(parent, dict):
                    parent = parent.get("nameWithOwner")

                repo_rows.append(
                    (
                        repo_id,
                        owner_id,
                        repo["name"],
                        repo["stars"],
                        repo["forks"],
                        repo["watchers"],
                        repo["isFork"],
                        repo["isArchived"],
                        repo["topicCount"],
                        repo["diskUsageKb"],
                        repo["pullRequests"],
                        repo["issues"],
                        repo["description"],
                        primary_id,
                        repo["createdAt"],
                        repo["pushedAt"],
                        repo["defaultBranchCommitCount"],
                        repo["license"],
                        repo["assignableUserCount"],
                        repo["codeOfConduct"],
                        repo["forkingAllowed"],
                        parent,
                    )
                )

                for lang in repo["languages"]:
                    language_id = get_id(languages, lang["name"])
                    language_links.append((language_id, repo_id, lang["size"]))

                for topic in repo["topics"]:
                    topic_id = get_id(topics, topic["name"])
                    topic_stars[topic_id] = topic["stars"]
                    topic_links.append((topic_id, repo_id))

            owner_rows = [(i, name) for name, i in owners.items()]
            language_rows = [(i, name) for name, i in languages.items()]
            topic_rows = [(i, name, topic_stars[i]) for name, i in topics.items()]

            tables = [
                ("app_repoowner", "id, name", owner_rows),
                ("app_language", "id, name", language_rows),
                ("app_topic", "id, name, stars", topic_rows),
                ("app_repo", REPO_COLUMNS, repo_rows),
                ("app_languagerepo", "language_id, repo_id, size", language_links),
                ("app_topicrepo", "topic_id, repo_id", topic_links),
            ]

            with transaction.atomic():
                with connection.cursor() as django_cursor:
                    cursor = django_cursor.cursor

                    names = ", ".join(table for table, _, _ in tables)
                    cursor.execute(f"TRUNCATE {names} RESTART IDENTITY")

                    for table, columns, rows in tables:
                        t = time.perf_counter()
                        with cursor.copy(
                            f"COPY {table} ({columns}) FROM STDIN"
                        ) as copy:
                            for row in rows:
                                copy.write_row(row)

                commit_start = time.perf_counter()

            print(f"всего: {time.perf_counter() - total:.2f} с")
        finally:
            gc.enable()
