from __future__ import annotations

from django.db import models

from apps.common.models import SoftDeleteModel


class Status(SoftDeleteModel):
    code = models.CharField(max_length=30, unique=True)
    name = models.CharField(max_length=120)
    description = models.TextField(blank=True)

    class Meta:
        db_table = "taxonomy_status"
        indexes = [models.Index(fields=["deleted", "code"], name="taxonomy_st_deleted_code_idx")]

    def __str__(self) -> str:
        return f"{self.code} - {self.name}"
