from django.db import models


class TimeStampedModel(models.Model):
    """Abstract base adding created/updated timestamps to every model in
    the project, so audit questions ("when was this added/changed?")
    always have an answer without extra migrations later."""

    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
        ordering = ["-created_at"]
