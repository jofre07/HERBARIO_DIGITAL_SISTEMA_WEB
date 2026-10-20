from __future__ import annotations

from typing import Any

from django.db import transaction

from apps.common.exceptions import ConflictError, NotFoundError
from apps.taxonomy.models import (
    CommonName,
    ConservationStatus,
    Family,
    Genus,
    Language,
    Species,
    Status,
    Translation,
)
from apps.taxonomy.repositories import (
    CommonNameRepository,
    ConservationStatusRepository,
    FamilyRepository,
    GenusRepository,
    LanguageRepository,
    SpeciesRepository,
    StatusRepository,
    TranslationRepository,
)


class FamilyService:
    def __init__(self, repository: FamilyRepository | None = None) -> None:
        self.repository = repository or FamilyRepository()

    @transaction.atomic
    def create(self, *, data: dict[str, Any]) -> Family:
        if self.repository.get_by_name(data["name"]):
            raise ConflictError(f"La familia '{data['name']}' ya existe.")
        return self.repository.create(name=data["name"], comment=data.get("comment", ""))

    @transaction.atomic
    def update(self, instance: Family, *, data: dict[str, Any]) -> Family:
        if "name" in data and data["name"] != instance.name:
            if self.repository.get_by_name(data["name"]):
                raise ConflictError(f"La familia '{data['name']}' ya existe.")
            instance.name = data["name"]
        if "comment" in data:
            instance.comment = data["comment"]
        return self.repository.save(instance)

    @transaction.atomic
    def soft_delete(self, instance: Family) -> None:
        self.repository.soft_delete(instance)


class GenusService:
    def __init__(self, repository: GenusRepository | None = None) -> None:
        self.repository = repository or GenusRepository()

    @transaction.atomic
    def create(self, *, data: dict[str, Any]) -> Genus:
        family = self._resolve_family(data["family"])
        if family is None:
            raise NotFoundError("No se encontró la familia.")
        if self.repository.get_by_name_and_family(data["name"], family.pk):
            raise ConflictError(f"El género '{data['name']}' ya existe en esta familia.")
        return self.repository.create(
            name=data["name"], family=family, comment=data.get("comment", "")
        )

    @transaction.atomic
    def update(self, instance: Genus, *, data: dict[str, Any]) -> Genus:
        family = instance.family
        if "family" in data:
            family = self._resolve_family(data["family"])
            if family is None:
                raise NotFoundError("No se encontró la familia.")
            instance.family = family
        name = data.get("name", instance.name)
        if name != instance.name or family.pk != instance.family_id:
            if self.repository.get_by_name_and_family(name, family.pk):
                raise ConflictError(f"El género '{name}' ya existe en esta familia.")
            instance.name = name
        if "comment" in data:
            instance.comment = data["comment"]
        return self.repository.save(instance)

    @transaction.atomic
    def soft_delete(self, instance: Genus) -> None:
        self.repository.soft_delete(instance)

    def _resolve_family(self, value: Family | int) -> Family | None:
        if isinstance(value, Family):
            return value
        return Family.objects.filter(pk=value).first()


class SpeciesService:
    def __init__(self, repository: SpeciesRepository | None = None) -> None:
        self.repository = repository or SpeciesRepository()

    @transaction.atomic
    def create(self, *, data: dict[str, Any]) -> Species:
        genus = self._resolve_genus(data["genus"])
        if genus is None:
            raise NotFoundError("No se encontró el género.")
        if self.repository.get_by_name_and_genus(data["name"], genus.pk):
            raise ConflictError(f"La especie '{data['name']}' ya existe en este género.")
        self._ensure_featured_capacity(is_featured=data.get("is_featured", False))
        return self.repository.create(
            name=data["name"],
            genus=genus,
            comment=data.get("comment", ""),
            is_featured=data.get("is_featured", False),
        )

    @transaction.atomic
    def update(self, instance: Species, *, data: dict[str, Any]) -> Species:
        genus = instance.genus
        if "genus" in data:
            genus = self._resolve_genus(data["genus"])
            if genus is None:
                raise NotFoundError("No se encontró el género.")
            instance.genus = genus
        name = data.get("name", instance.name)
        if name != instance.name or genus.pk != instance.genus_id:
            if self.repository.get_by_name_and_genus(name, genus.pk):
                raise ConflictError(f"La especie '{name}' ya existe en este género.")
            instance.name = name
        if "comment" in data:
            instance.comment = data["comment"]
        if "is_featured" in data:
            self._ensure_featured_capacity(
                is_featured=data["is_featured"],
                instance=instance,
            )
            instance.is_featured = data["is_featured"]
        return self.repository.save(instance)

    @transaction.atomic
    def soft_delete(self, instance: Species) -> None:
        self.repository.soft_delete(instance)

    def _resolve_genus(self, value: Genus | int) -> Genus | None:
        if isinstance(value, Genus):
            return value
        return Genus.objects.filter(pk=value).first()

    def _ensure_featured_capacity(
        self,
        *,
        is_featured: bool,
        instance: Species | None = None,
    ) -> None:
        if not is_featured or (instance is not None and instance.is_featured):
            return
        if Species.objects.filter(is_featured=True).count() >= 4:
            raise ConflictError(
                "Solo se permiten cuatro especies destacadas. Desmarca una antes de destacar otra."
            )


class LanguageService:
    def __init__(self, repository: LanguageRepository | None = None) -> None:
        self.repository = repository or LanguageRepository()

    @transaction.atomic
    def create(self, *, data: dict[str, Any]) -> Language:
        code = data["code"].strip().lower()
        if self.repository.get_by_code(code):
            raise ConflictError(f"El idioma con código '{code}' ya existe.")
        return self.repository.create(
            code=code,
            name=data["name"],
            native_name=data.get("native_name", ""),
        )

    @transaction.atomic
    def update(self, instance: Language, *, data: dict[str, Any]) -> Language:
        if "code" in data:
            code = data["code"].strip().lower()
            if code != instance.code and self.repository.get_by_code(code):
                raise ConflictError(f"El idioma con código '{code}' ya existe.")
            instance.code = code
        if "name" in data:
            instance.name = data["name"]
        if "native_name" in data:
            instance.native_name = data["native_name"]
        return self.repository.save(instance)

    @transaction.atomic
    def soft_delete(self, instance: Language) -> None:
        self.repository.soft_delete(instance)


class StatusService:
    def __init__(self, repository: StatusRepository | None = None) -> None:
        self.repository = repository or StatusRepository()

    @transaction.atomic
    def create(self, *, data: dict[str, Any]) -> Status:
        code = data["code"].strip().upper()
        if self.repository.get_by_code(code):
            raise ConflictError(f"El estado con código '{code}' ya existe.")
        return self.repository.create(
            code=code,
            name=data["name"],
            description=data.get("description", ""),
        )

    @transaction.atomic
    def update(self, instance: Status, *, data: dict[str, Any]) -> Status:
        if "code" in data:
            code = data["code"].strip().upper()
            if code != instance.code and self.repository.get_by_code(code):
                raise ConflictError(f"El estado con código '{code}' ya existe.")
            instance.code = code
        if "name" in data:
            instance.name = data["name"]
        if "description" in data:
            instance.description = data["description"]
        return self.repository.save(instance)

    @transaction.atomic
    def soft_delete(self, instance: Status) -> None:
        self.repository.soft_delete(instance)


class CommonNameService:
    def __init__(self, repository: CommonNameRepository | None = None) -> None:
        self.repository = repository or CommonNameRepository()

    @transaction.atomic
    def create(self, *, data: dict[str, Any]) -> CommonName:
        species = self._resolve_species(data["species"])
        if species is None:
            raise NotFoundError("No se encontró la especie.")
        language = self._resolve_language(data["language"])
        if language is None:
            raise NotFoundError("No se encontró el idioma.")
        return self.repository.create(
            species=species,
            language=language,
            common_name=data["common_name"],
            dialect=data.get("dialect", ""),
            region=CommonName.DEFAULT_REGION,
        )

    @transaction.atomic
    def update(self, instance: CommonName, *, data: dict[str, Any]) -> CommonName:
        if "species" in data:
            species = self._resolve_species(data["species"])
            if species is None:
                raise NotFoundError("No se encontró la especie.")
            instance.species = species
        if "language" in data:
            language = self._resolve_language(data["language"])
            if language is None:
                raise NotFoundError("No se encontró el idioma.")
            instance.language = language
        for field in ("common_name", "dialect"):
            if field in data:
                setattr(instance, field, data[field])
        instance.region = CommonName.DEFAULT_REGION
        return self.repository.save(instance)

    @transaction.atomic
    def soft_delete(self, instance: CommonName) -> None:
        self.repository.soft_delete(instance)

    def _resolve_species(self, value: Species | int) -> Species | None:
        if isinstance(value, Species):
            return value
        return Species.objects.filter(pk=value).first()

    def _resolve_language(self, value: Language | int) -> Language | None:
        if isinstance(value, Language):
            return value
        return Language.objects.filter(pk=value).first()


class TranslationService:
    def __init__(self, repository: TranslationRepository | None = None) -> None:
        self.repository = repository or TranslationRepository()

    @transaction.atomic
    def create(self, *, data: dict[str, Any]) -> Translation:
        common_name = self._resolve_common_name(data["common_name"])
        if common_name is None:
            raise NotFoundError("No se encontró el nombre común.")
        language = self._resolve_language(data["language"])
        if language is None:
            raise NotFoundError("No se encontró el idioma.")
        return self.repository.create(
            common_name=common_name,
            language=language,
            translated_name=data["translated_name"],
        )

    @transaction.atomic
    def update(self, instance: Translation, *, data: dict[str, Any]) -> Translation:
        if "common_name" in data:
            common_name = self._resolve_common_name(data["common_name"])
            if common_name is None:
                raise NotFoundError("No se encontró el nombre común.")
            instance.common_name = common_name
        if "language" in data:
            language = self._resolve_language(data["language"])
            if language is None:
                raise NotFoundError("No se encontró el idioma.")
            instance.language = language
        if "translated_name" in data:
            instance.translated_name = data["translated_name"]
        return self.repository.save(instance)

    @transaction.atomic
    def soft_delete(self, instance: Translation) -> None:
        self.repository.soft_delete(instance)

    def _resolve_common_name(self, value: CommonName | int) -> CommonName | None:
        if isinstance(value, CommonName):
            return value
        return CommonName.objects.filter(pk=value).first()

    def _resolve_language(self, value: Language | int) -> Language | None:
        if isinstance(value, Language):
            return value
        return Language.objects.filter(pk=value).first()


class ConservationStatusService:
    def __init__(self, repository: ConservationStatusRepository | None = None) -> None:
        self.repository = repository or ConservationStatusRepository()

    @transaction.atomic
    def create(self, *, data: dict[str, Any]) -> ConservationStatus:
        species = self._resolve_species(data["species"])
        if species is None:
            raise NotFoundError("No se encontró la especie.")
        status = self._resolve_status(data["status"])
        if status is None:
            raise NotFoundError("No se encontró el estado de conservación.")
        if self.repository.get_by_species_and_status(species.pk, status.pk):
            raise ConflictError("El estado de conservación ya está asignado a esta especie.")
        return self.repository.create(species=species, status=status)

    @transaction.atomic
    def update(self, instance: ConservationStatus, *, data: dict[str, Any]) -> ConservationStatus:
        if "species" in data:
            species = self._resolve_species(data["species"])
            if species is None:
                raise NotFoundError("No se encontró la especie.")
            instance.species = species
        if "status" in data:
            status = self._resolve_status(data["status"])
            if status is None:
                raise NotFoundError("No se encontró el estado de conservación.")
            instance.status = status
        if self.repository.get_by_species_and_status(instance.species_id, instance.status_id):
            existing = self.repository.get_by_species_and_status(
                instance.species_id,
                instance.status_id,
            )
            if existing and existing.pk != instance.pk:
                raise ConflictError("El estado de conservación ya está asignado a esta especie.")
        return self.repository.save(instance)

    @transaction.atomic
    def soft_delete(self, instance: ConservationStatus) -> None:
        self.repository.soft_delete(instance)

    def _resolve_species(self, value: Species | int) -> Species | None:
        if isinstance(value, Species):
            return value
        return Species.objects.filter(pk=value).first()

    def _resolve_status(self, value: Status | int) -> Status | None:
        if isinstance(value, Status):
            return value
        return Status.objects.filter(pk=value).first()
