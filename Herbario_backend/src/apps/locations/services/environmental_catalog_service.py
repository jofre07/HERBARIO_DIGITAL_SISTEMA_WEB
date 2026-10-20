from __future__ import annotations

from typing import Any

from django.db import transaction

from apps.common.exceptions import ConflictError
from apps.locations.models import Climate, Habitat


class EnvironmentalCatalogService:
    model = None

    @transaction.atomic
    def create(self, *, data: dict[str, Any]):
        return self.model.objects.create(name=data["name"])

    @transaction.atomic
    def update(self, instance, *, data: dict[str, Any]):
        if "name" in data:
            instance.name = data["name"]
        instance.save()
        return instance

    @transaction.atomic
    def soft_delete(self, instance) -> None:
        related_managers = [
            getattr(instance, relation, None)
            for relation in ("location_links", "specimen_links")
        ]
        if any(manager is not None and manager.exists() for manager in related_managers):
            raise ConflictError("No se puede eliminar un catálogo que está en uso.")
        instance.soft_delete()


class ClimateService(EnvironmentalCatalogService):
    model = Climate


class HabitatService(EnvironmentalCatalogService):
    model = Habitat
