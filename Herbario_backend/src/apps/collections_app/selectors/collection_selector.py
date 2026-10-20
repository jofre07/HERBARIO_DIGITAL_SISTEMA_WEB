from __future__ import annotations

from django.db.models import Prefetch, Q, QuerySet

from apps.collections_app.models import Collection


def list_collections_for_api(
    params: dict | None = None, *, include_unpublished: bool = False
) -> QuerySet[Collection]:
    from apps.specimens.models import Specimen

    params = params or {}
    specimen_qs = Specimen.objects.all()
    if not include_unpublished:
        specimen_qs = specimen_qs.filter(is_published=True)
    specimen_qs = specimen_qs.select_related(
        "species__genus__family"
    ).prefetch_related(
        "species__conservation_statuses__status",
        "location_links__location",
        "images__variants",
    )
    qs = Collection.objects.all()
    if not include_unpublished:
        qs = qs.filter(specimens__is_published=True)
    qs = qs.prefetch_related(
        Prefetch("specimens", queryset=specimen_qs)
    ).order_by("name")
    if collection_type := params.get("collection_type"):
        qs = qs.filter(collection_type=collection_type)
    if family_name := params.get("family_name"):
        qs = qs.filter(
            specimens__species__genus__family__name__icontains=family_name,
            **({} if include_unpublished else {"specimens__is_published": True}),
        )
    if location_name := params.get("location_name"):
        qs = qs.filter(
            specimens__location_links__location__name__icontains=location_name,
            **({} if include_unpublished else {"specimens__is_published": True}),
        )
    if conservation := params.get("conservation_status"):
        status_filter = (
            Q(specimens__species__conservation_statuses__status__code__icontains=conservation)
            | Q(specimens__species__conservation_statuses__status__name__icontains=conservation)
        )
        if not include_unpublished:
            status_filter &= Q(specimens__is_published=True)
        qs = qs.filter(status_filter)
    return qs.distinct()


def get_collection_by_id(
    collection_id: int, *, include_unpublished: bool = False
) -> Collection | None:
    return list_collections_for_api(include_unpublished=include_unpublished).filter(
        pk=collection_id
    ).first()
