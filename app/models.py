from django.db import models


class RepoOwner(models.Model):
    name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.name


class Language(models.Model):
    name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.name


class Topic(models.Model):
    name = models.CharField(max_length=255, unique=True)
    stars = models.PositiveBigIntegerField()

    def __str__(self):
        return self.name


class Repo(models.Model):
    owner = models.ForeignKey(
        RepoOwner, on_delete=models.CASCADE, related_name="repositories"
    )
    name = models.CharField(max_length=255)

    stars = models.PositiveIntegerField(null=True, blank=True)
    forks = models.PositiveIntegerField(null=True, blank=True)
    watchers = models.PositiveIntegerField(null=True, blank=True)
    is_fork = models.BooleanField(null=True, blank=True)
    is_archived = models.BooleanField(null=True, blank=True)
    topics_count = models.PositiveIntegerField(null=True, blank=True)
    disk_usage = models.PositiveIntegerField(null=True, blank=True)
    pull_requests = models.PositiveIntegerField(null=True, blank=True)
    issues = models.PositiveIntegerField(null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    primary_language = models.ForeignKey(
        Language,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="primary",
        db_constraint=False,
        db_index=False,
    )
    created_at = models.DateTimeField(null=True, blank=True)
    pushed_at = models.DateTimeField(null=True, blank=True)
    default_branch_commit = models.PositiveIntegerField(null=True, blank=True)
    license = models.CharField(max_length=255, null=True, blank=True)
    assignable_user_count = models.PositiveIntegerField(null=True, blank=True)
    code_of_conduct = models.CharField(max_length=255, null=True, blank=True)
    forking_allowed = models.BooleanField(null=True, blank=True)
    parent_name_with_owner = models.CharField(max_length=255, null=True, blank=True)
 
    languages = models.ManyToManyField(
        Language, through="LanguageRepo", related_name="repos"
    )
    topics = models.ManyToManyField(Topic, through="TopicRepo", related_name="repos")

    def __str__(self):
        return self.name

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["owner", "name"], name="unique_owner_name")
        ]


class LanguageRepo(models.Model):
    language = models.ForeignKey(
        Language, on_delete=models.CASCADE, db_constraint=False, db_index=False
    )
    repo = models.ForeignKey(
        Repo, on_delete=models.CASCADE, db_constraint=False, db_index=False
    )
    size = models.PositiveBigIntegerField()


class TopicRepo(models.Model):
    topic = models.ForeignKey(
        Topic, on_delete=models.CASCADE, db_constraint=False, db_index=False
    )
    repo = models.ForeignKey(
        Repo, on_delete=models.CASCADE, db_constraint=False, db_index=False
    )
