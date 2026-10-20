from __future__ import annotations

from apps.collections_app.models import Collection
from apps.common.repositories.base_repository import BaseRepository


class CollectionRepository(BaseRepository[Collection]):
    model = Collection

    def get_by_name(self, name: str) -> Collection | None:
        return Collection.objects.filter(name=name).first()

    def create(self, **data) -> Collection:
        specimens = data.pop("specimens", None)
        collection = Collection.objects.create(**data)
        if specimens is not None:
            collection.specimens.set(specimens)
        return collection

    def save(self, collection: Collection, *, specimens=None) -> Collection:
        collection.save()
        if specimens is not None:
            collection.specimens.set(specimens)
        return collection

    def soft_delete(self, collection: Collection) -> None:
        collection.soft_delete()
