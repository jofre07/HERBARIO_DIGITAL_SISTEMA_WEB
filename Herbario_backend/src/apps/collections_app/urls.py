from django.urls import include, path
from rest_framework.routers import DefaultRouter

from apps.collections_app.api.viewsets import CollectionViewSet

router = DefaultRouter()
router.register("", CollectionViewSet, basename="collections")

urlpatterns = [path("", include(router.urls))]
