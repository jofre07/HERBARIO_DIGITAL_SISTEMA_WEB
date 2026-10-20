from __future__ import annotations

from apps.common.repositories.base_repository import BaseRepository
from apps.taxonomy.models import Family


class FamilyRepository(BaseRepository[Family]):
    model = Family

    def get_by_name(self, name: str) -> Family | None:
        return Family.objects.filter(name=name).first()

    def create(self, **data) -> Family:
        return Family.objects.create(**data)

    def save(self, instance: Family) -> Family:
        instance.save()
        return instance

    def soft_delete(self, instance: Family) -> None:
        instance.soft_delete()
