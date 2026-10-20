from __future__ import annotations

from pathlib import Path
from uuid import uuid4

from django.db import models

from apps.common.models import SoftDeleteModel


def herbarium_image_upload_path(instance: "HerbariumImage", filename: str) -> str:
    extension = Path(filename).suffix.lower()
    return f"specimens/{instance.specimen_id}/images/{uuid4().hex}{extension}"


def herbarium_variant_upload_path(instance: "HerbariumImageVariant", filename: str) -> str:
    return f"specimens/{instance.image.specimen_id}/images/{instance.variant}/{uuid4().hex}.webp"


class HerbariumImage(SoftDeleteModel):
    specimen = models.ForeignKey(
        "specimens.Specimen",
        on_delete=models.PROTECT,
        related_name="images",
    )
    image = models.ImageField(upload_to=herbarium_image_upload_path, blank=True, null=True)
    url = models.URLField(blank=True)
    credit = models.CharField(max_length=255, blank=True)

    class Meta:
        db_table = "media_herbariumimage"
        indexes = [models.Index(fields=["deleted", "-created_at"])]

    def __str__(self) -> str:
        return self.image.name if self.image else self.url


class HerbariumImageVariant(models.Model):
    THUMBNAIL = "thumbnail"
    MEDIUM = "medium"
    LARGE = "large"
    VARIANT_CHOICES = (
        (THUMBNAIL, "Miniatura"),
        (MEDIUM, "Mediana"),
        (LARGE, "Grande"),
    )

    image = models.ForeignKey(
        HerbariumImage,
        on_delete=models.CASCADE,
        related_name="variants",
    )
    variant = models.CharField(max_length=16, choices=VARIANT_CHOICES)
    file = models.ImageField(upload_to=herbarium_variant_upload_path)
    width = models.PositiveIntegerField()
    height = models.PositiveIntegerField()
    file_size = models.PositiveIntegerField()
    format = models.CharField(max_length=10, default="webp")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "media_herbariumimagevariant"
        constraints = [
            models.UniqueConstraint(
                fields=["image", "variant"],
                name="unique_herbarium_image_variant",
            )
        ]

    def __str__(self) -> str:
        return f"{self.image_id}:{self.variant}"
