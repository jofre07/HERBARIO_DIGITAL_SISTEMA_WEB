from django.urls import include, path
from rest_framework.routers import DefaultRouter

from apps.taxonomy.api.views.catalog_view import SpeciesCatalogView
from apps.taxonomy.api.viewsets import (
    CommonNameViewSet,
    ConservationStatusViewSet,
    FamilyViewSet,
    GenusViewSet,
    LanguageViewSet,
    SpeciesViewSet,
    StatusViewSet,
    TranslationViewSet,
)

router = DefaultRouter()
router.register("families", FamilyViewSet, basename="families")
router.register("genera", GenusViewSet, basename="genera")
router.register("species", SpeciesViewSet, basename="species")
router.register("languages", LanguageViewSet, basename="languages")
router.register("statuses", StatusViewSet, basename="statuses")
router.register("common-names", CommonNameViewSet, basename="common-names")
router.register("translations", TranslationViewSet, basename="translations")
router.register(
    "conservation-statuses", ConservationStatusViewSet, basename="conservation-statuses"
)

urlpatterns = [
    path("catalog/species/", SpeciesCatalogView.as_view(), name="species-catalog"),
    path("", include(router.urls)),
]
