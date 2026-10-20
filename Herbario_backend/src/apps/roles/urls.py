from django.urls import include, path
from rest_framework.routers import DefaultRouter

from apps.roles.api.viewsets import PermissionViewSet, RoleViewSet

router = DefaultRouter()
router.register("permissions", PermissionViewSet, basename="permissions")
router.register("", RoleViewSet, basename="roles")

urlpatterns = [path("", include(router.urls))]
