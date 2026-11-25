from django.conf import settings
from django.db import models


class AgentRun(models.Model):
    class Status(models.TextChoices):
        RUNNING = "running", "Running"
        DONE = "done", "Done"
        FAILED = "failed", "Failed"

    agent = models.CharField(max_length=50)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="agent_runs"
    )
    input = models.JSONField()                              # what we asked
    steps = models.JSONField(default=list, blank=True)      # which lookups the AI requested
    output = models.JSONField(null=True, blank=True)        # what it produced
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.RUNNING)
    error = models.TextField(blank=True)
    input_tokens = models.PositiveIntegerField(default=0)   # cost tracking
    output_tokens = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.agent} #{self.pk} ({self.status})"