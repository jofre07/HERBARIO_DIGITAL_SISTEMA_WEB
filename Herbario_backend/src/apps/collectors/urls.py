from django.urls import include, path
from rest_framework.routers import DefaultRouter

from apps.collectors.api.viewsets import CollectorViewSet

router = DefaultRouter()
router.register("", CollectorViewSet, basename="collectors")

urlpatterns = [path("", include(router.urls))]
