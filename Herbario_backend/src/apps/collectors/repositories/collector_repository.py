from __future__ import annotations

from apps.collectors.models import Collector
from apps.common.repositories.base_repository import BaseRepository


class CollectorRepository(BaseRepository[Collector]):
    model = Collector

    def get_by_name(self, name: str) -> Collector | None:
        return Collector.objects.filter(name=name).first()

    def create(self, **data) -> Collector:
        return Collector.objects.create(**data)

    def save(self, instance: Collector) -> Collector:
        instance.save()
        return instance

    def soft_delete(self, instance: Collector) -> None:
        instance.soft_delete()
