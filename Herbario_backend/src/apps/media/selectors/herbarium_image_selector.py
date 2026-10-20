from __future__ import annotations

from django.db.models import QuerySet

from apps.media.models import HerbariumImage


def list_media_for_api(*, include_unpublished: bool = False) -> QuerySet[HerbariumImage]:
    qs = HerbariumImage.objects.all()
    if not include_unpublished:
        qs = qs.filter(specimen__is_published=True)
    return (
        qs.select_related(
            "specimen",
            "specimen__species",
            "specimen__species__genus",
            "specimen__species__genus__family",
        )
        .prefetch_related(
            "variants",
            "specimen__location_links__location",
            "specimen__species__conservation_statuses__status",
        )
        .order_by("-created_at")
    )


def get_image_by_id(
    image_id: int, *, include_unpublished: bool = False
) -> HerbariumImage | None:
    return list_media_for_api(include_unpublished=include_unpublished).filter(
        pk=image_id
    ).first()
