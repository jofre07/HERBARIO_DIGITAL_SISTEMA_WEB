from __future__ import annotations

from django.db import models

from apps.common.models import SoftDeleteModel


class CommonName(SoftDeleteModel):
    DEFAULT_REGION = "Costa"

    species = models.ForeignKey(
        "taxonomy.Species",
        on_delete=models.PROTECT,
        related_name="common_names",
    )
    language = models.ForeignKey(
        "taxonomy.Language",
        on_delete=models.PROTECT,
        related_name="common_names",
    )
    common_name = models.CharField(max_length=255)
    dialect = models.CharField(max_length=120, blank=True)
    region = models.CharField(max_length=120, default=DEFAULT_REGION, editable=False)

    class Meta:
        db_table = "taxonomy_commonname"
        indexes = [
            models.Index(fields=["deleted", "common_name"]),
            models.Index(fields=["species"]),
        ]

    def __str__(self) -> str:
        return self.common_name
