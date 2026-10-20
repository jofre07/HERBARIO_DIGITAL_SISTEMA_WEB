from __future__ import annotations

from apps.common.repositories.base_repository import BaseRepository
from apps.media.models import HerbariumImage


class HerbariumImageRepository(BaseRepository[HerbariumImage]):
    model = HerbariumImage

    def create(self, **data) -> HerbariumImage:
        return HerbariumImage.objects.create(**data)

    def save(self, image: HerbariumImage) -> HerbariumImage:
        image.save()
        return image

    def soft_delete(self, image: HerbariumImage) -> None:
        image.soft_delete()
