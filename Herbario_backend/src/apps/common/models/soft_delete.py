from __future__ import annotations

from django.db import models
from django.utils import timezone

from apps.common.managers.soft_delete_manager import AllObjectsManager, SoftDeleteManager
from apps.common.models.base import BaseModel


class SoftDeleteModel(BaseModel):
    deleted = models.BooleanField(default=False, db_index=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    objects = SoftDeleteManager()
    all_objects = AllObjectsManager()

    class Meta:
        abstract = True

    def soft_delete(self) -> None:
        self.deleted = True
        self.deleted_at = timezone.now()
        self.save(update_fields=["deleted", "deleted_at", "updated_at"])

    def restore(self) -> None:
        self.deleted = False
        self.deleted_at = None
        self.save(update_fields=["deleted", "deleted_at", "updated_at"])
