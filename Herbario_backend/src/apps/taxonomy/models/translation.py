from __future__ import annotations

from django.db import models

from apps.common.models import SoftDeleteModel


class Translation(SoftDeleteModel):
    common_name = models.ForeignKey(
        "taxonomy.CommonName",
        on_delete=models.PROTECT,
        related_name="translations",
    )
    language = models.ForeignKey(
        "taxonomy.Language",
        on_delete=models.PROTECT,
        related_name="translations",
    )
    translated_name = models.CharField(max_length=255)

    class Meta:
        db_table = "taxonomy_translation"
        unique_together = ("common_name", "language")

    def __str__(self) -> str:
        return f"{self.translated_name} [{self.language.code}]"
