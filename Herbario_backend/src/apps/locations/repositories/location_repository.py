from __future__ import annotations

from apps.common.repositories.base_repository import BaseRepository
from apps.locations.models import Location


class LocationRepository(BaseRepository[Location]):
    model = Location

    def create(self, **data) -> Location:
        return Location.objects.create(**data)

    def save(self, instance: Location) -> Location:
        instance.save()
        return instance

    def soft_delete(self, instance: Location) -> None:
        instance.soft_delete()
