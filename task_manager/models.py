from django.conf import settings
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.urls import reverse


class Position(models.Model):
    name = models.CharField(max_length=255, unique=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class Worker(AbstractUser):
    position = models.ForeignKey(
        Position,
        on_delete=models.SET_NULL,
        related_name="workers",
        null=True,
        blank=True
    )


    class Meta:
        verbose_name = "worker"
        verbose_name_plural = "workers"
        ordering = ["username"]

    def __str__(self):
        full_name = f"{self.first_name} {self.last_name}".strip()
        return f"{self.username} ({full_name})" if full_name else self.username

    def get_absolute_url(self):
        return reverse("task_manager:worker-detail", kwargs={"pk": self.pk})


class TaskType(models.Model):
    name = models.CharField(max_length=255, unique=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class Task(models.Model):
    PRIORITY_CHOICES = [
        ("Urgent", "Urgent"),
        ("High", "High"),
        ("Medium", "Medium"),
        ("Low", "Low"),
    ]

    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    deadline = models.DateField(null=True, blank=True)
    is_completed = models.BooleanField(default=False)
    priority = models.CharField(
        max_length=10,
        choices=PRIORITY_CHOICES,
        default="Medium"
    )
    task_type = models.ForeignKey(
        TaskType,
        on_delete=models.SET_NULL,
        related_name="tasks",
        null=True,
        blank=True
    )
    assignees = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name="tasks",
        blank=True
    )

    class Meta:
        ordering = ["deadline"]
        verbose_name = "task"
        verbose_name_plural = "tasks"

    def __str__(self):
        return f"{self.name} ({self.priority})"
