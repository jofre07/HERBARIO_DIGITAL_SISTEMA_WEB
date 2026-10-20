from __future__ import annotations

from django.db import models

from apps.common.models import SoftDeleteModel


class ClimateHabitat(SoftDeleteModel):
    def __init__(self, *args, **kwargs):
        from apps.locations.models.climate import Climate
        from apps.locations.models.habitat import Habitat

        if isinstance(kwargs.get("climate"), str):
            name = kwargs["climate"].strip()
            kwargs["climate"] = Climate.objects.get_or_create(name=name)[0] if name else None
        if isinstance(kwargs.get("habitat"), str):
            name = kwargs["habitat"].strip()
            kwargs["habitat"] = Habitat.objects.get_or_create(name=name)[0] if name else None
        super().__init__(*args, **kwargs)

    location = models.ForeignKey(
        "locations.Location",
        on_delete=models.PROTECT,
        related_name="climate_habitats",
    )
    climate = models.ForeignKey(
        "locations.Climate",
        on_delete=models.PROTECT,
        related_name="location_links",
        blank=True,
        null=True,
    )
    habitat = models.ForeignKey(
        "locations.Habitat",
        on_delete=models.PROTECT,
        related_name="location_links",
        blank=True,
        null=True,
    )

    class Meta:
        db_table = "locations_climatehabitat"
        indexes = [models.Index(fields=["deleted", "climate"]), models.Index(fields=["habitat"])]

    def __str__(self) -> str:
        return f"{self.location_id}: {self.climate or '-'} / {self.habitat or '-'}"
