from __future__ import annotations

from typing import Any

from django.db import transaction

from apps.collections_app.models import Collection
from apps.collections_app.repositories import CollectionRepository
from apps.common.exceptions import ConflictError


class CollectionService:
    def __init__(self, repository: CollectionRepository | None = None) -> None:
        self.repository = repository or CollectionRepository()

    @transaction.atomic
    def create(self, *, data: dict[str, Any]) -> Collection:
        name = data["name"]
        if self.repository.get_by_name(name):
            raise ConflictError(f"La colección '{name}' ya existe.")

        return self.repository.create(
            name=name,
            description=data.get("description", ""),
            collection_type=data.get("collection_type", Collection.CollectionType.GENERAL),
            specimens=data.get("specimens"),
        )

    @transaction.atomic
    def update(self, collection: Collection, *, data: dict[str, Any]) -> Collection:
        if "name" in data and data["name"] != collection.name:
            existing = self.repository.get_by_name(data["name"])
            if existing and existing.pk != collection.pk:
                raise ConflictError(f"La colección '{data['name']}' ya existe.")
            collection.name = data["name"]

        if "description" in data:
            collection.description = data["description"]
        if "collection_type" in data:
            collection.collection_type = data["collection_type"]

        specimens = data.get("specimens")
        return self.repository.save(collection, specimens=specimens)

    @transaction.atomic
    def soft_delete(self, collection: Collection) -> None:
        self.repository.soft_delete(collection)
