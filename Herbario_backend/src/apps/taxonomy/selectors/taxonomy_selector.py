from __future__ import annotations

from django.db.models import Prefetch, Q, QuerySet

from apps.taxonomy.models import (
    CommonName,
    ConservationStatus,
    Family,
    Genus,
    Language,
    Species,
    Status,
    Translation,
)


def list_families_for_api() -> QuerySet[Family]:
    return Family.objects.order_by("name")


def list_genera_for_api() -> QuerySet[Genus]:
    return Genus.objects.select_related("family").order_by("name")


def list_species_for_api() -> QuerySet[Species]:
    return Species.objects.select_related("genus", "genus__family").order_by("name")


def list_languages_for_api() -> QuerySet[Language]:
    return Language.objects.order_by("name")


def list_statuses_for_api() -> QuerySet[Status]:
    return Status.objects.order_by("code")


def list_species_catalog_for_api(params: dict | None = None) -> QuerySet[Species]:
    from apps.specimens.models import Specimen

    params = params or {}
    published_specimens = Specimen.objects.filter(is_published=True).prefetch_related(
        "images__variants",
        "location_links__location",
        "location_links__climate",
        "location_links__habitat",
        "species__conservation_statuses__status",
    )
    qs = (
        Species.objects.filter(specimens__is_published=True)
        .select_related("genus", "genus__family")
        .prefetch_related(
            "common_names",
            "conservation_statuses__status",
            Prefetch("specimens", queryset=published_specimens),
        )
        .order_by("name")
    )
    if family := params.get("family"):
        qs = qs.filter(genus__family_id=family)
    if family_name := params.get("family_name"):
        qs = qs.filter(genus__family__name__icontains=family_name)
    if genus := params.get("genus"):
        qs = qs.filter(genus_id=genus)
    if genus_name := params.get("genus_name"):
        qs = qs.filter(genus__name__icontains=genus_name)
    if species := params.get("species"):
        qs = qs.filter(pk=species)
    if species_name := params.get("species_name"):
        qs = qs.filter(name__icontains=species_name)
    if str(params.get("featured", "")).lower() in {"1", "true", "yes"}:
        qs = qs.filter(is_featured=True)
    if name := params.get("q"):
        qs = qs.filter(
            Q(name__icontains=name)
            | Q(genus__name__icontains=name)
            | Q(genus__family__name__icontains=name)
            | Q(common_names__common_name__icontains=name)
        )
    if common_name := params.get("common_name"):
        qs = qs.filter(common_names__common_name__icontains=common_name)
    if conservation := params.get("conservation_status"):
        qs = qs.filter(
            Q(conservation_statuses__status__code__icontains=conservation)
            | Q(conservation_statuses__status__name__icontains=conservation)
        )
    if habitat := params.get("habitat"):
        qs = qs.filter(
            specimens__is_published=True,
            specimens__location_links__habitat__name__icontains=habitat,
        )
    if climate := params.get("climate"):
        qs = qs.filter(
            specimens__is_published=True,
            specimens__location_links__climate__name__icontains=climate,
        )
    if location := params.get("location_name"):
        qs = qs.filter(
            specimens__is_published=True,
            specimens__location_links__location__name__icontains=location,
        )
    ordering = params.get("ordering", "name")
    if ordering in {
        "name",
        "-name",
        "created_at",
        "-created_at",
        "genus__family__name",
    }:
        qs = qs.order_by(ordering)
    return qs.distinct()


def list_common_names_for_api() -> QuerySet[CommonName]:
    return CommonName.objects.select_related("species", "language").order_by("common_name")


def list_translations_for_api() -> QuerySet[Translation]:
    return Translation.objects.select_related("common_name", "language").order_by("id")


def list_conservation_statuses_for_api() -> QuerySet[ConservationStatus]:
    return ConservationStatus.objects.select_related("species", "status").order_by("id")
