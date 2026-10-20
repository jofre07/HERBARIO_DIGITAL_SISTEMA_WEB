from __future__ import annotations

from django.db import models

from apps.common.models import SoftDeleteModel


class Family(SoftDeleteModel):
    name = models.CharField(max_length=255, unique=True)
    comment = models.TextField(blank=True)

    class Meta:
        db_table = "taxonomy_family"
        indexes = [models.Index(fields=["deleted", "name"])]

    def __str__(self) -> str:
        return self.name
