from __future__ import annotations

from django.db import models

from apps.common.models import SoftDeleteModel


class Genus(SoftDeleteModel):
    name = models.CharField(max_length=255)
    family = models.ForeignKey(
        "taxonomy.Family",
        on_delete=models.PROTECT,
        related_name="genera",
    )
    comment = models.TextField(blank=True)

    class Meta:
        db_table = "taxonomy_genus"
        unique_together = ("name", "family")
        indexes = [models.Index(fields=["deleted", "name"])]

    def __str__(self) -> str:
        return self.name
