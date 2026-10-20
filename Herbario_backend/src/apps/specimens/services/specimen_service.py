from __future__ import annotations

from typing import Any

from django.db import transaction

from apps.collectors.models import Collector
from apps.common.exceptions import ConflictError, NotFoundError
from apps.locations.models import Location
from apps.specimens.models import Specimen, SpecimenLocation
from apps.specimens.repositories import SpecimenRepository
from apps.taxonomy.models import Species


class SpecimenService:
    def __init__(self, repository: SpecimenRepository | None = None) -> None:
        self.repository = repository or SpecimenRepository()

    @transaction.atomic
    def create(self, *, data: dict[str, Any]) -> Specimen:
        catalog_code = data["catalog_code"]
        if self.repository.get_by_catalog_code(catalog_code):
            raise ConflictError(f"Ya existe un espécimen con el código '{catalog_code}'.")

        species = self._resolve_species(data["species"])
        if species is None:
            raise NotFoundError("No se encontró la especie.")

        collector = self._resolve_collector(data.get("collector"))
        if data.get("collector") is not None and collector is None:
            raise NotFoundError("No se encontró el colector.")

        locations = data.pop("locations", [])
        specimen = self.repository.create(
            catalog_code=catalog_code,
            is_published=data.get("is_published", False),
            collection_date=data.get("collection_date"),
            collection_number=data.get("collection_number", ""),
            morphological_description=data.get("morphological_description", ""),
            species=species,
            collector=collector,
        )
        self._sync_locations(specimen, locations)
        return specimen

    @transaction.atomic
    def update(self, specimen: Specimen, *, data: dict[str, Any]) -> Specimen:
        if "catalog_code" in data and data["catalog_code"] != specimen.catalog_code:
            existing = self.repository.get_by_catalog_code(data["catalog_code"])
            if existing and existing.pk != specimen.pk:
                raise ConflictError(
                    f"Ya existe un espécimen con el código '{data['catalog_code']}'."
                )
            specimen.catalog_code = data["catalog_code"]

        if "species" in data:
            species = self._resolve_species(data["species"])
            if species is None:
                raise NotFoundError("No se encontró la especie.")
            specimen.species = species

        if "collector" in data:
            collector = self._resolve_collector(data["collector"])
            if data["collector"] is not None and collector is None:
                raise NotFoundError("No se encontró el colector.")
            specimen.collector = collector

        locations = data.pop("locations", None)

        for field in (
            "is_published",
            "collection_date",
            "collection_number",
            "morphological_description",
        ):
            if field in data:
                setattr(specimen, field, data[field])

        specimen = self.repository.save(specimen)
        if locations is not None:
            self._sync_locations(specimen, locations)
        return specimen

    @transaction.atomic
    def soft_delete(self, specimen: Specimen) -> None:
        self.repository.soft_delete(specimen)

    def _resolve_species(self, value: Species | int) -> Species | None:
        if isinstance(value, Species):
            return value
        return Species.objects.filter(pk=value).first()

    def _resolve_collector(self, value: Collector | int | None) -> Collector | None:
        if value is None:
            return None
        if isinstance(value, Collector):
            return value
        return Collector.objects.filter(pk=value).first()

    def _sync_locations(self, specimen: Specimen, locations: list[dict[str, Any]]) -> None:
        for item in locations:
            if "new_location" in item:
                item["location"] = Location.objects.create(**item.pop("new_location"))
        desired_ids = {item["location"].pk for item in locations}
        specimen.location_links.exclude(location_id__in=desired_ids).delete()
        specimen.location_links.update(is_primary=False)
        for item in locations:
            SpecimenLocation.objects.update_or_create(
                specimen=specimen,
                location=item["location"],
                defaults={
                    "climate": item.get("climate"),
                    "habitat": item.get("habitat"),
                    "comment": item.get("comment", ""),
                    "marker_icon": item.get("marker_icon", "plant"),
                    "is_primary": item.get("is_primary", False),
                    "order": item.get("order", 1),
                },
            )
