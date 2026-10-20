from __future__ import annotations

from django.db import models

from apps.common.models import SoftDeleteModel


class Collection(SoftDeleteModel):
    class CollectionType(models.TextChoices):
        DESTACADA = "destacada", "Especies destacadas"
        AMENAZADA = "amenazada", "Especies amenazadas"
        RECIENTE = "reciente", "Nuevos registros"
        LOCAL = "local", "Interés local"
        GENERAL = "general", "General"

    name = models.CharField(max_length=120, unique=True)
    description = models.TextField(blank=True)
    collection_type = models.CharField(
        max_length=20,
        choices=CollectionType.choices,
        default=CollectionType.GENERAL,
    )
    specimens = models.ManyToManyField(
        "specimens.Specimen",
        related_name="collections",
        blank=True,
    )

    class Meta:
        db_table = "collections_app_collection"
        indexes = [
            models.Index(fields=["deleted", "name"]),
            models.Index(fields=["collection_type"]),
        ]

    def __str__(self) -> str:
        return self.name
