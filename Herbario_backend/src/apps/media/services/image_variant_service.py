from __future__ import annotations

from io import BytesIO
from pathlib import Path

from django.core.files.base import ContentFile
from django.db import transaction
from PIL import Image, ImageOps

from apps.media.models import HerbariumImage, HerbariumImageVariant


class ImageVariantService:
    SPECS = {
        HerbariumImageVariant.THUMBNAIL: (320, 70),
        HerbariumImageVariant.MEDIUM: (800, 78),
        HerbariumImageVariant.LARGE: (1600, 84),
    }

    def generate(self, image: HerbariumImage) -> list[HerbariumImageVariant]:
        if not image.image:
            return []

        previous_files = [
            (variant.file.storage, variant.file.name)
            for variant in image.variants.all()
            if variant.file
        ]
        generated_files: list[tuple] = []
        generated: list[HerbariumImageVariant] = []

        try:
            image.image.open("rb")
            with Image.open(image.image) as source:
                normalized = ImageOps.exif_transpose(source)
                normalized.load()
                for variant_name, (max_dimension, quality) in self.SPECS.items():
                    rendered = normalized.copy()
                    rendered.thumbnail((max_dimension, max_dimension), Image.Resampling.LANCZOS)
                    if rendered.mode not in {"RGB", "RGBA"}:
                        output_mode = "RGBA" if "transparency" in rendered.info else "RGB"
                        rendered = rendered.convert(output_mode)

                    output = BytesIO()
                    rendered.save(output, format="WEBP", quality=quality, method=6)
                    content = output.getvalue()
                    filename = f"{Path(image.image.name).stem}-{variant_name}.webp"
                    variant, _ = HerbariumImageVariant.objects.update_or_create(
                        image=image,
                        variant=variant_name,
                        defaults={
                            "width": rendered.width,
                            "height": rendered.height,
                            "file_size": len(content),
                            "format": "webp",
                        },
                    )
                    variant.file.save(filename, ContentFile(content), save=True)
                    generated_files.append((variant.file.storage, variant.file.name))
                    generated.append(variant)
        except Exception:
            for storage, name in generated_files:
                if name and storage.exists(name):
                    storage.delete(name)
            raise
        finally:
            image.image.close()

        getattr(image, "_prefetched_objects_cache", {}).pop("variants", None)
        generated_names = {variant.file.name for variant in generated}
        for storage, name in previous_files:
            if name and name not in generated_names and storage.exists(name):
                transaction.on_commit(
                    lambda storage=storage, name=name: storage.delete(name)
                )
        return generated

    def delete_files(self, image: HerbariumImage) -> None:
        for variant in image.variants.all():
            if variant.file and variant.file.storage.exists(variant.file.name):
                variant.file.storage.delete(variant.file.name)


def image_asset_url(image: HerbariumImage, variant: str = HerbariumImageVariant.MEDIUM) -> str:
    optimized = next(
        (item for item in image.variants.all() if item.variant == variant and item.file),
        None,
    )
    if optimized:
        return optimized.file.url
    if image.image:
        return image.image.url
    return image.url


def absolute_image_asset_url(
    image: HerbariumImage,
    request=None,
    variant: str = HerbariumImageVariant.MEDIUM,
) -> str:
    url = image_asset_url(image, variant)
    return request.build_absolute_uri(url) if request and url.startswith("/") else url
