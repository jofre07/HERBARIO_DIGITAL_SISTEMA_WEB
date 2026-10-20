from __future__ import annotations

from django.db import models

from apps.common.models import BaseModel


class SpecimenLocation(BaseModel):
    MARKER_ICON_CHOICES = [
        ("plant", "Planta"),
        ("flower", "Flor"),
        ("tree", "Árbol"),
        ("leaf", "Hoja"),
        ("herb", "Hierba"),
    ]

    def __init__(self, *args, **kwargs):
        from apps.locations.models import Climate, Habitat

        if isinstance(kwargs.get("climate"), str):
            name = kwargs["climate"].strip()
            kwargs["climate"] = Climate.objects.get_or_create(name=name)[0] if name else None
        if isinstance(kwargs.get("habitat"), str):
            name = kwargs["habitat"].strip()
            kwargs["habitat"] = Habitat.objects.get_or_create(name=name)[0] if name else None
        super().__init__(*args, **kwargs)

    specimen = models.ForeignKey(
        "specimens.Specimen",
        on_delete=models.CASCADE,
        related_name="location_links",
    )
    location = models.ForeignKey(
        "locations.Location",
        on_delete=models.PROTECT,
        related_name="specimen_links",
    )
    climate = models.ForeignKey(
        "locations.Climate",
        on_delete=models.PROTECT,
        related_name="specimen_links",
        blank=True,
        null=True,
    )
    habitat = models.ForeignKey(
        "locations.Habitat",
        on_delete=models.PROTECT,
        related_name="specimen_links",
        blank=True,
        null=True,
    )
    comment = models.TextField(blank=True)
    marker_icon = models.CharField(
        max_length=20,
        choices=MARKER_ICON_CHOICES,
        default="plant",
    )
    is_primary = models.BooleanField(default=False)
    order = models.PositiveIntegerField(default=1)

    class Meta:
        db_table = "specimens_specimenlocation"
        ordering = ["order", "id"]
        constraints = [
            models.UniqueConstraint(
                fields=["specimen", "location"],
                name="unique_specimen_location",
            ),
            models.UniqueConstraint(
                fields=["specimen"],
                condition=models.Q(is_primary=True),
                name="unique_primary_location_per_specimen",
            ),
        ]
        indexes = [
            models.Index(fields=["specimen", "order"]),
            models.Index(fields=["location", "is_primary"]),
        ]

    def __str__(self) -> str:
        return f"{self.specimen_id}: {self.location_id}"
