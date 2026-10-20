from __future__ import annotations

from django.db import models

from apps.common.models import SoftDeleteModel


class ConservationStatus(SoftDeleteModel):
    species = models.ForeignKey(
        "taxonomy.Species",
        on_delete=models.PROTECT,
        related_name="conservation_statuses",
    )
    status = models.ForeignKey(
        "taxonomy.Status",
        on_delete=models.PROTECT,
        related_name="species_statuses",
    )

    class Meta:
        db_table = "taxonomy_conservationstatus"
        unique_together = ("species", "status")
        indexes = [
            models.Index(fields=["deleted", "status"], name="taxonomy_cs_deleted_status_idx")
        ]

    def __str__(self) -> str:
        return f"{self.species_id}: {self.status}"
