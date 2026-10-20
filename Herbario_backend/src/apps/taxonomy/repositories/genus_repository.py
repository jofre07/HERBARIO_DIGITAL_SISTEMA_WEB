from __future__ import annotations

from apps.common.repositories.base_repository import BaseRepository
from apps.taxonomy.models import Genus


class GenusRepository(BaseRepository[Genus]):
    model = Genus

    def get_by_name_and_family(self, name: str, family_id: int) -> Genus | None:
        return Genus.objects.filter(name=name, family_id=family_id).first()

    def create(self, **data) -> Genus:
        return Genus.objects.create(**data)

    def save(self, instance: Genus) -> Genus:
        instance.save()
        return instance

    def soft_delete(self, instance: Genus) -> None:
        instance.soft_delete()
