from __future__ import annotations

from drf_spectacular.utils import extend_schema
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.collections_app.models import Collection
from apps.collectors.models import Collector
from apps.common.selectors import list_popular_search_terms
from apps.locations.models import Location
from apps.roles.permissions import HasRolePermission
from apps.roles.roles import READ_ROLES
from apps.specimens.models import Specimen, SpecimenLocation
from apps.taxonomy.models import CommonName, Family, Genus, Species, Status


def _unique_text_options(values) -> list[str]:
    unique: dict[str, str] = {}
    for raw_value in values:
        value = raw_value.strip() if raw_value else ""
        if value:
            unique.setdefault(value.casefold(), value)
    return sorted(unique.values(), key=str.casefold)


@extend_schema(tags=["Sistema"])
class PublicFilterOptionsView(APIView):
    permission_classes = [IsAuthenticated, HasRolePermission]
    required_roles = READ_ROLES

    def get(self, request):
        published_specimens = Specimen.objects.filter(is_published=True)
        families = (
            Family.objects.filter(genera__species__specimens__is_published=True)
            .distinct()
            .order_by("name")
        )
        genera = (
            Genus.objects.filter(species__specimens__is_published=True)
            .distinct()
            .select_related("family")
            .order_by("name")
        )
        species = (
            Species.objects.filter(specimens__is_published=True)
            .distinct()
            .select_related("genus", "genus__family")
            .order_by("name")
        )
        links = SpecimenLocation.objects.filter(specimen__is_published=True)
        collections = Collection.objects.filter(specimens__is_published=True).distinct()

        return Response(
            {
                "families": list(families.values_list("name", flat=True)),
                "genera": [
                    {"name": genus.name, "family_name": genus.family.name} for genus in genera
                ],
                "species": [
                    {
                        "name": item.name,
                        "genus_name": item.genus.name,
                        "family_name": item.genus.family.name,
                    }
                    for item in species
                ],
                "collectors": list(
                    Collector.objects.filter(specimens__is_published=True)
                    .distinct()
                    .order_by("name")
                    .values_list("name", flat=True)
                ),
                "locations": list(
                    Location.objects.filter(specimen_links__specimen__is_published=True)
                    .distinct()
                    .order_by("name")
                    .values_list("name", flat=True)
                ),
                "habitats": _unique_text_options(links.values_list("habitat__name", flat=True)),
                "climates": _unique_text_options(links.values_list("climate__name", flat=True)),
                "conservation_statuses": list(
                    Status.objects.filter(species_statuses__species__specimens__is_published=True)
                    .distinct()
                    .order_by("name")
                    .values_list("name", flat=True)
                ),
                "common_names": list(
                    CommonName.objects.filter(species__specimens__is_published=True)
                    .order_by("common_name")
                    .values_list("common_name", flat=True)
                    .distinct()
                ),
                "image_types": [{"value": "specimen", "label": "Espécimen"}],
                "popular_searches": list_popular_search_terms(),
                "collection_categories": [
                    {
                        "value": value,
                        "label": label,
                        "count": collections.filter(collection_type=value).count(),
                    }
                    for value, label in Collection.CollectionType.choices
                ],
                "collection_specimen_count": published_specimens.filter(collections__isnull=False)
                .distinct()
                .count(),
            }
        )
