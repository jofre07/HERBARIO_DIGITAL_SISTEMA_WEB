from __future__ import annotations

from typing import Any

from django.db import transaction

from apps.common.exceptions import NotFoundError, ValidationError
from apps.media.models import HerbariumImage
from apps.media.repositories import HerbariumImageRepository
from apps.media.services.image_variant_service import ImageVariantService
from apps.specimens.models import Specimen


class HerbariumImageService:
    MAX_IMAGES_PER_SPECIMEN = 5

    def __init__(self, repository: HerbariumImageRepository | None = None) -> None:
        self.repository = repository or HerbariumImageRepository()
        self.variant_service = ImageVariantService()

    @transaction.atomic
    def create(self, *, data: dict[str, Any]) -> HerbariumImage:
        specimen = self._resolve_specimen(data["specimen"])
        if specimen is None:
            raise NotFoundError("No se encontró el espécimen.")

        specimen = Specimen.objects.select_for_update().get(pk=specimen.pk)
        self._validate_image_limit(specimen)

        created = self.repository.create(
            specimen=specimen,
            image=data.get("image"),
            url=data.get("url", ""),
            credit=data.get("credit", ""),
        )
        if created.image:
            try:
                self.variant_service.generate(created)
            except Exception:
                if created.image.storage.exists(created.image.name):
                    created.image.storage.delete(created.image.name)
                raise
        return created

    @transaction.atomic
    def update(self, image: HerbariumImage, *, data: dict[str, Any]) -> HerbariumImage:
        if "specimen" in data:
            specimen = self._resolve_specimen(data["specimen"])
            if specimen is None:
                raise NotFoundError("No se encontró el espécimen.")
            specimen = Specimen.objects.select_for_update().get(pk=specimen.pk)
            self._validate_image_limit(specimen, exclude_image=image)
            image.specimen = specimen

        previous_file_name = image.image.name if image.image else ""
        if "image" in data:
            image.image = data["image"]
        if "url" in data:
            image.url = data["url"]
        if "credit" in data:
            image.credit = data["credit"]

        saved_image = self.repository.save(image)
        if "image" in data and saved_image.image:
            try:
                self.variant_service.generate(saved_image)
            except Exception:
                if (
                    saved_image.image.name != previous_file_name
                    and saved_image.image.storage.exists(saved_image.image.name)
                ):
                    saved_image.image.storage.delete(saved_image.image.name)
                raise
        if previous_file_name and "image" in data and previous_file_name != image.image.name:
            storage = image.image.storage
            transaction.on_commit(lambda: storage.delete(previous_file_name))
        return saved_image

    @transaction.atomic
    def soft_delete(self, image: HerbariumImage) -> None:
        file_name = image.image.name if image.image else ""
        storage = image.image.storage if image.image else None
        variant_files = [
            (variant.file.storage, variant.file.name)
            for variant in image.variants.all()
            if variant.file
        ]
        image.variants.all().delete()
        self.repository.soft_delete(image)
        if file_name and storage:
            transaction.on_commit(lambda: storage.delete(file_name))
        for variant_storage, variant_name in variant_files:
            transaction.on_commit(
                lambda storage=variant_storage, name=variant_name: storage.delete(name)
            )

    def _resolve_specimen(self, specimen_value: Specimen | int) -> Specimen | None:
        if isinstance(specimen_value, Specimen):
            return specimen_value
        return Specimen.objects.filter(pk=specimen_value).first()

    def _validate_image_limit(
        self,
        specimen: Specimen,
        *,
        exclude_image: HerbariumImage | None = None,
    ) -> None:
        images = HerbariumImage.objects.filter(specimen=specimen)
        if exclude_image:
            images = images.exclude(pk=exclude_image.pk)
        if images.count() >= self.MAX_IMAGES_PER_SPECIMEN:
            raise ValidationError("Cada espécimen puede tener un máximo de 5 imágenes.")
