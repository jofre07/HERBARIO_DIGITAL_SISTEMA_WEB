from __future__ import annotations

from django.db import models

from apps.common.models import SoftDeleteModel


class Language(SoftDeleteModel):
    code = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=120)
    native_name = models.CharField(max_length=120, blank=True)

    class Meta:
        db_table = "taxonomy_language"
        indexes = [models.Index(fields=["deleted", "code"])]

    def __str__(self) -> str:
        return self.native_name or self.name
