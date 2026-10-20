from __future__ import annotations

from typing import Any

from django.db import transaction

from apps.common.exceptions import ConflictError
from apps.locations.models import Location
from apps.locations.repositories import LocationRepository


class LocationService:
    def __init__(self, repository: LocationRepository | None = None) -> None:
        self.repository = repository or LocationRepository()

    @transaction.atomic
    def create(self, *, data: dict[str, Any]) -> Location:
        return self.repository.create(
            name=data["name"],
            latitude=data["latitude"],
            longitude=data["longitude"],
            comment=data.get("comment", ""),
        )

    @transaction.atomic
    def update(self, location: Location, *, data: dict[str, Any]) -> Location:
        for field in ("name", "latitude", "longitude", "comment"):
            if field in data:
                setattr(location, field, data[field])
        return self.repository.save(location)

    @transaction.atomic
    def soft_delete(self, location: Location) -> None:
        if location.specimen_links.filter(specimen__deleted=False).exists():
            raise ConflictError("No se puede eliminar una ubicación asociada a especímenes.")
        self.repository.soft_delete(location)
