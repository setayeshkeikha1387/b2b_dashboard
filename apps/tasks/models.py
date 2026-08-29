"""Task model — the actionable work items owners work through day to
day, optionally linked back to the Risk/Control that generated them
(e.g. 'remediate this control by Friday')."""
from __future__ import annotations

from django.conf import settings
from django.db import models
from django.urls import reverse
from django.utils import timezone

from apps.common.models import TimeStampedModel


class Task(TimeStampedModel):
    class Status(models.TextChoices):
        TODO = "todo", "To do"
        IN_PROGRESS = "in_progress", "In progress"
        DONE = "done", "Done"

    class Priority(models.TextChoices):
        LOW = "low", "Low"
        MEDIUM = "medium", "Medium"
        HIGH = "high", "High"

    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="tasks",
    )
    due_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=16, choices=Status.choices, default=Status.TODO, db_index=True)
    priority = models.CharField(max_length=16, choices=Priority.choices, default=Priority.MEDIUM)
    completed_at = models.DateTimeField(null=True, blank=True)

    # Optional links back to the GRC domain — a task is often "go fix
    # this control" or "investigate this risk". Both are optional so
    # Task also works as a general-purpose to-do independent of GRC.
    related_risk = models.ForeignKey(
        "grc.Risk", null=True, blank=True, on_delete=models.SET_NULL, related_name="tasks",
    )
    related_control = models.ForeignKey(
        "grc.Control", null=True, blank=True, on_delete=models.SET_NULL, related_name="tasks",
    )

    class Meta(TimeStampedModel.Meta):
        indexes = [models.Index(fields=["status", "due_date"])]
        verbose_name = "Task"

    def __str__(self) -> str:
        return self.title

    def get_absolute_url(self) -> str:
        return reverse("tasks:task_detail", args=[self.pk])

    @property
    def is_overdue(self) -> bool:
        return bool(
            self.due_date and self.status != self.Status.DONE and self.due_date < timezone.localdate()
        )

    def mark_done(self) -> None:
        """Domain behaviour kept on the model (not scattered across
        views) so both the web UI and any future API/management command
        transition a task the same way."""
        self.status = self.Status.DONE
        self.completed_at = timezone.now()
        self.save(update_fields=["status", "completed_at", "updated_at"])
