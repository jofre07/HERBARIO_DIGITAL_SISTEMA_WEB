from __future__ import annotations

from django.conf import settings
from django.db import models

from apps.common.models import SoftDeleteModel


class AuditLog(SoftDeleteModel):
    action = models.CharField(max_length=255)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="audit_logs",
    )
    timestamp = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        db_table = "users_auditlog"
        ordering = ["-timestamp"]

    def __str__(self) -> str:
        return f"{self.timestamp}: {self.action}"
