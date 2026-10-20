from __future__ import annotations

from django.db import models

from apps.common.models import SoftDeleteModel


class Specimen(SoftDeleteModel):
    catalog_code = models.CharField(max_length=40, unique=True)
    is_published = models.BooleanField(default=False, db_index=True)
    collection_date = models.DateField(null=True, blank=True)
    collection_number = models.CharField(max_length=80, blank=True)
    morphological_description = models.TextField(blank=True)
    species = models.ForeignKey(
        "taxonomy.Species",
        on_delete=models.PROTECT,
        related_name="specimens",
    )
    collector = models.ForeignKey(
        "collectors.Collector",
        on_delete=models.PROTECT,
        related_name="specimens",
        null=True,
        blank=True,
    )
    locations = models.ManyToManyField(
        "locations.Location",
        through="specimens.SpecimenLocation",
        related_name="specimens",
        blank=True,
    )

    class Meta:
        db_table = "specimens_specimen"
        indexes = [
            models.Index(fields=["deleted", "catalog_code"]),
            models.Index(fields=["collection_date"]),
        ]

    def __str__(self) -> str:
        return self.catalog_code
