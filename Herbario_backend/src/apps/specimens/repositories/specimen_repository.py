from __future__ import annotations

from apps.common.repositories.base_repository import BaseRepository
from apps.specimens.models import Specimen


class SpecimenRepository(BaseRepository[Specimen]):
    model = Specimen

    def get_by_catalog_code(self, catalog_code: str) -> Specimen | None:
        return Specimen.objects.filter(catalog_code=catalog_code).first()

    def create(self, **data) -> Specimen:
        return Specimen.objects.create(**data)

    def save(self, specimen: Specimen) -> Specimen:
        specimen.save()
        return specimen

    def soft_delete(self, specimen: Specimen) -> None:
        specimen.soft_delete()
