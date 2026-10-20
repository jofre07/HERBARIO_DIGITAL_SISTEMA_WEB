from __future__ import annotations

from apps.common.repositories.base_repository import BaseRepository
from apps.taxonomy.models import CommonName, ConservationStatus, Language, Status, Translation


class LanguageRepository(BaseRepository[Language]):
    model = Language

    def create(self, **data) -> Language:
        return Language.objects.create(**data)

    def save(self, instance: Language) -> Language:
        instance.save()
        return instance

    def soft_delete(self, instance: Language) -> None:
        instance.soft_delete()

    def get_by_code(self, code: str) -> Language | None:
        return Language.objects.filter(code=code).first()


class StatusRepository(BaseRepository[Status]):
    model = Status

    def create(self, **data) -> Status:
        return Status.objects.create(**data)

    def save(self, instance: Status) -> Status:
        instance.save()
        return instance

    def soft_delete(self, instance: Status) -> None:
        instance.soft_delete()

    def get_by_code(self, code: str) -> Status | None:
        return Status.objects.filter(code=code).first()


class CommonNameRepository(BaseRepository[CommonName]):
    model = CommonName

    def create(self, **data) -> CommonName:
        return CommonName.objects.create(**data)

    def save(self, instance: CommonName) -> CommonName:
        instance.save()
        return instance

    def soft_delete(self, instance: CommonName) -> None:
        instance.soft_delete()


class TranslationRepository(BaseRepository[Translation]):
    model = Translation

    def create(self, **data) -> Translation:
        return Translation.objects.create(**data)

    def save(self, instance: Translation) -> Translation:
        instance.save()
        return instance

    def soft_delete(self, instance: Translation) -> None:
        instance.soft_delete()


class ConservationStatusRepository(BaseRepository[ConservationStatus]):
    model = ConservationStatus

    def create(self, **data) -> ConservationStatus:
        return ConservationStatus.objects.create(**data)

    def save(self, instance: ConservationStatus) -> ConservationStatus:
        instance.save()
        return instance

    def soft_delete(self, instance: ConservationStatus) -> None:
        instance.soft_delete()

    def get_by_species_and_status(
        self,
        species_id: int,
        status_id: int,
    ) -> ConservationStatus | None:
        return ConservationStatus.objects.filter(
            species_id=species_id,
            status_id=status_id,
        ).first()
