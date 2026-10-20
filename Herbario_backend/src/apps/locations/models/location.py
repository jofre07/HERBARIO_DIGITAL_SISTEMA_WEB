from __future__ import annotations

from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from apps.common.models import SoftDeleteModel


class Location(SoftDeleteModel):
    name = models.CharField(max_length=255)
    latitude = models.DecimalField(
        max_digits=10,
        decimal_places=8,
        validators=[MinValueValidator(-90), MaxValueValidator(90)],
    )
    longitude = models.DecimalField(
        max_digits=11,
        decimal_places=8,
        validators=[MinValueValidator(-180), MaxValueValidator(180)],
    )
    comment = models.TextField(blank=True)

    class Meta:
        db_table = "locations_location"
        indexes = [
            models.Index(fields=["deleted", "name"]),
            models.Index(fields=["latitude", "longitude"]),
        ]

    def __str__(self) -> str:
        return self.name
