from __future__ import annotations

from apps.common.repositories.base_repository import BaseRepository
from apps.locations.models import ClimateHabitat


class ClimateHabitatRepository(BaseRepository[ClimateHabitat]):
    model = ClimateHabitat

    def create(self, **data) -> ClimateHabitat:
        return ClimateHabitat.objects.create(**data)

    def save(self, instance: ClimateHabitat) -> ClimateHabitat:
        instance.save()
        return instance

    def soft_delete(self, instance: ClimateHabitat) -> None:
        instance.soft_delete()
