from __future__ import annotations

from django.db import models

from apps.common.models import SoftDeleteModel


class Species(SoftDeleteModel):
    name = models.CharField(max_length=255)
    genus = models.ForeignKey(
        "taxonomy.Genus",
        on_delete=models.PROTECT,
        related_name="species",
    )
    comment = models.TextField(blank=True)
    is_featured = models.BooleanField(default=False, db_index=True)

    class Meta:
        db_table = "taxonomy_species"
        unique_together = ("name", "genus")
        indexes = [models.Index(fields=["deleted", "name"])]

    def __str__(self) -> str:
        return self.name
