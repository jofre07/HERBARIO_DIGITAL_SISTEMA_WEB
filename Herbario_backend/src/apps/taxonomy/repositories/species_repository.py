from __future__ import annotations

from apps.common.repositories.base_repository import BaseRepository
from apps.taxonomy.models import Species


class SpeciesRepository(BaseRepository[Species]):
    model = Species

    def get_by_name_and_genus(self, name: str, genus_id: int) -> Species | None:
        return Species.objects.filter(name=name, genus_id=genus_id).first()

    def create(self, **data) -> Species:
        return Species.objects.create(**data)

    def save(self, instance: Species) -> Species:
        instance.save()
        return instance

    def soft_delete(self, instance: Species) -> None:
        instance.soft_delete()
