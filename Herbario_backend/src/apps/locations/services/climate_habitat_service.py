from __future__ import annotations

from typing import Any

from django.db import transaction

from apps.common.exceptions import NotFoundError
from apps.locations.models import ClimateHabitat, Location
from apps.locations.repositories import ClimateHabitatRepository


class ClimateHabitatService:
    def __init__(self, repository: ClimateHabitatRepository | None = None) -> None:
        self.repository = repository or ClimateHabitatRepository()

    @transaction.atomic
    def create(self, *, data: dict[str, Any]) -> ClimateHabitat:
        location = self._resolve_location(data["location"])
        if location is None:
            raise NotFoundError("No se encontró la ubicación.")
        return self.repository.create(
            location=location,
            climate=data.get("climate"),
            habitat=data.get("habitat"),
        )

    @transaction.atomic
    def update(self, record: ClimateHabitat, *, data: dict[str, Any]) -> ClimateHabitat:
        if "location" in data:
            location = self._resolve_location(data["location"])
            if location is None:
                raise NotFoundError("No se encontró la ubicación.")
            record.location = location
        if "climate" in data:
            record.climate = data["climate"]
        if "habitat" in data:
            record.habitat = data["habitat"]
        return self.repository.save(record)

    @transaction.atomic
    def soft_delete(self, record: ClimateHabitat) -> None:
        self.repository.soft_delete(record)

    def _resolve_location(self, value: Location | int) -> Location | None:
        if isinstance(value, Location):
            return value
        return Location.objects.filter(pk=value).first()
