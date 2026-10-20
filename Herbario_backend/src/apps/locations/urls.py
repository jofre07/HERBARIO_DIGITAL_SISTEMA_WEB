from django.urls import include, path
from rest_framework.routers import DefaultRouter

from apps.locations.api.views.map_view import MapPointsView
from apps.locations.api.viewsets import (
    ClimateHabitatViewSet,
    ClimateViewSet,
    HabitatViewSet,
    LocationViewSet,
)

router = DefaultRouter()
router.register("climate-habitats", ClimateHabitatViewSet, basename="climate-habitats")
router.register("climates", ClimateViewSet, basename="climates")
router.register("habitats", HabitatViewSet, basename="habitats")
router.register("", LocationViewSet, basename="locations")

urlpatterns = [
    path("map/points/", MapPointsView.as_view(), name="map-points"),
    path("", include(router.urls)),
]
