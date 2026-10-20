from django.urls import include, path
from rest_framework import viewsets
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.routers import DefaultRouter

from apps.collections_app.api.viewsets.collection_viewset import CollectionViewSet
from apps.collections_app.selectors import list_collections_for_api
from apps.common.api.views.filter_options_view import PublicFilterOptionsView
from apps.common.api.views.search_query_view import SearchQueryView
from apps.common.api.views.stats_view import HerbariumStatsView
from apps.common.api.viewsets.mixins import EncodedLookupMixin
from apps.locations.api.views.map_view import MapPointsView
from apps.locations.api.viewsets.location_viewset import (
    ClimateHabitatViewSet,
    ClimateViewSet,
    HabitatViewSet,
    LocationViewSet,
)
from apps.media.api.viewsets.herbarium_image_viewset import HerbariumImageViewSet
from apps.media.api.serializers import HerbariumImageSerializer
from apps.collectors.api.viewsets.collector_viewset import CollectorViewSet
from apps.specimens.api.viewsets import PublicSpecimenViewSet
from apps.taxonomy.api.serializers import SpeciesSerializer
from apps.taxonomy.api.views.catalog_view import PublicSpeciesCatalogDetailView, PublicSpeciesImagesView, SpeciesCatalogView
from apps.taxonomy.api.viewsets.taxonomy_viewsets import (
    CommonNameViewSet,
    ConservationStatusViewSet,
    FamilyViewSet,
    GenusViewSet,
    LanguageViewSet,
    StatusViewSet,
    TranslationViewSet,
)
from apps.taxonomy.selectors import list_species_for_api


class PublicSpeciesViewSet(EncodedLookupMixin, viewsets.ReadOnlyModelViewSet):
    serializer_class = SpeciesSerializer
    permission_classes = [AllowAny]
    search_fields = ["name", "genus__name", "genus__family__name"]

    def get_queryset(self):
        return list_species_for_api().filter(specimens__is_published=True).distinct()


class PublicCollectionViewSet(CollectionViewSet):
    permission_classes = [AllowAny]
    http_method_names = ["get", "head", "options"]

    def get_queryset(self):
        return list_collections_for_api(
            dict(self.request.query_params.items()), include_unpublished=False
        )


class PublicImageViewSet(HerbariumImageViewSet):
    permission_classes = [AllowAny]
    http_method_names = ["get", "head", "options"]

    def can_include_unpublished(self, request) -> bool:
        return False

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        serializer = HerbariumImageSerializer(
            page if page is not None else queryset,
            many=True,
            context=self.get_serializer_context(),
        )
        if page is not None:
            return self.get_paginated_response(serializer.data)
        return Response(serializer.data)


class PublicReadOnlyMixin:
    permission_classes = [AllowAny]
    http_method_names = ["get", "head", "options"]


class PublicFamilyViewSet(PublicReadOnlyMixin, FamilyViewSet):
    pass


class PublicGenusViewSet(PublicReadOnlyMixin, GenusViewSet):
    pass


class PublicLanguageViewSet(PublicReadOnlyMixin, LanguageViewSet):
    pass


class PublicStatusViewSet(PublicReadOnlyMixin, StatusViewSet):
    pass


class PublicCommonNameViewSet(PublicReadOnlyMixin, CommonNameViewSet):
    pass


class PublicTranslationViewSet(PublicReadOnlyMixin, TranslationViewSet):
    pass


class PublicConservationStatusViewSet(PublicReadOnlyMixin, ConservationStatusViewSet):
    pass


class PublicCollectorViewSet(PublicReadOnlyMixin, CollectorViewSet):
    pass


class PublicLocationViewSet(PublicReadOnlyMixin, LocationViewSet):
    pass


class PublicClimateHabitatViewSet(PublicReadOnlyMixin, ClimateHabitatViewSet):
    pass


class PublicClimateViewSet(PublicReadOnlyMixin, ClimateViewSet):
    pass


class PublicHabitatViewSet(PublicReadOnlyMixin, HabitatViewSet):
    pass


class PublicMapPointsView(MapPointsView):
    permission_classes = [AllowAny]


class PublicSpeciesCatalogView(SpeciesCatalogView):
    permission_classes = [AllowAny]


class PublishedStatsView(HerbariumStatsView):
    permission_classes = [AllowAny]
    public_only = True


class PublishedFilterOptionsView(PublicFilterOptionsView):
    permission_classes = [AllowAny]


router = DefaultRouter()
router.register("specimens", PublicSpecimenViewSet, basename="public-specimens")
router.register("taxonomy/species", PublicSpeciesViewSet, basename="public-species")
router.register("collections", PublicCollectionViewSet, basename="public-collections")
router.register("media", PublicImageViewSet, basename="public-media")
router.register("taxonomy/families", PublicFamilyViewSet, basename="public-families")
router.register("taxonomy/genera", PublicGenusViewSet, basename="public-genera")
router.register("taxonomy/languages", PublicLanguageViewSet, basename="public-languages")
router.register("taxonomy/statuses", PublicStatusViewSet, basename="public-statuses")
router.register("taxonomy/common-names", PublicCommonNameViewSet, basename="public-common-names")
router.register("taxonomy/translations", PublicTranslationViewSet, basename="public-translations")
router.register("taxonomy/conservation-statuses", PublicConservationStatusViewSet, basename="public-conservation-statuses")
router.register("collectors", PublicCollectorViewSet, basename="public-collectors")
router.register("locations/climate-habitats", PublicClimateHabitatViewSet, basename="public-climate-habitats")
router.register("locations/climates", PublicClimateViewSet, basename="public-climates")
router.register("locations/habitats", PublicHabitatViewSet, basename="public-habitats")
router.register("locations", PublicLocationViewSet, basename="public-locations")

urlpatterns = [
    path("stats/", PublishedStatsView.as_view(), name="public-stats"),
    path("filter-options/", PublishedFilterOptionsView.as_view(), name="public-filter-options"),
    path("searches/", SearchQueryView.as_view(), name="public-searches"),
    path("map/points/", PublicMapPointsView.as_view(), name="public-map-points"),
    path("catalog/species/", PublicSpeciesCatalogView.as_view(), name="public-species-catalog"),
    path("catalog/species/<str:pk>/", PublicSpeciesCatalogDetailView.as_view(), name="public-species-catalog-detail"),
    path("catalog/species/<str:pk>/images/", PublicSpeciesImagesView.as_view(), name="public-species-images"),
    path("content/", include("apps.site_content.public_urls")),
    path("", include(router.urls)),
]
