from __future__ import annotations

from typing import Any

from django.db import transaction

from apps.collectors.models import Collector
from apps.collectors.repositories import CollectorRepository
from apps.common.exceptions import ConflictError


class CollectorService:
    def __init__(self, repository: CollectorRepository | None = None) -> None:
        self.repository = repository or CollectorRepository()

    @transaction.atomic
    def create(self, *, data: dict[str, Any]) -> Collector:
        if self.repository.get_by_name(data["name"]):
            raise ConflictError(f"El colector '{data['name']}' ya existe.")
        return self.repository.create(name=data["name"], comment=data.get("comment", ""))

    @transaction.atomic
    def update(self, collector: Collector, *, data: dict[str, Any]) -> Collector:
        if "name" in data and data["name"] != collector.name:
            existing = self.repository.get_by_name(data["name"])
            if existing and existing.pk != collector.pk:
                raise ConflictError(f"El colector '{data['name']}' ya existe.")
            collector.name = data["name"]
        if "comment" in data:
            collector.comment = data["comment"]
        return self.repository.save(collector)

    @transaction.atomic
    def soft_delete(self, collector: Collector) -> None:
        self.repository.soft_delete(collector)
