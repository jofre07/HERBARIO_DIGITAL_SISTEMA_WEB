from django.urls import include, path
from rest_framework.routers import DefaultRouter

from apps.specimens.api.viewsets import SpecimenViewSet

router = DefaultRouter()
router.register("", SpecimenViewSet, basename="specimens")

urlpatterns = [
    path("", include(router.urls)),
]
