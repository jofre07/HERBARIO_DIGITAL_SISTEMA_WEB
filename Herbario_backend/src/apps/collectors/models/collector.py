from __future__ import annotations

from django.db import models

from apps.common.models import SoftDeleteModel


class Collector(SoftDeleteModel):
    name = models.CharField(max_length=255, unique=True)
    comment = models.TextField(blank=True)

    class Meta:
        db_table = "collectors_collector"
        indexes = [models.Index(fields=["deleted", "name"])]

    def __str__(self) -> str:
        return self.name
