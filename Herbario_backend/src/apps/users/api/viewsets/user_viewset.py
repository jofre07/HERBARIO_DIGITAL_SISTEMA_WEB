from __future__ import annotations

from drf_spectacular.utils import extend_schema
from rest_framework import mixins, status, viewsets
from rest_framework.response import Response

from apps.common.api.viewsets.mixins import DomainErrorResponseMixin, EncodedLookupMixin
from apps.common.exceptions import DomainError
from apps.roles.permissions import HasRolePermission
from apps.roles.roles import ADMIN_ONLY_ROLES
from apps.users.api.serializers import UserCreateSerializer, UserSerializer, UserUpdateSerializer
from apps.users.selectors import list_users_for_api
from apps.users.services import UserService


@extend_schema(tags=["Usuarios"])
class UserViewSet(
    EncodedLookupMixin,
    DomainErrorResponseMixin,
    mixins.CreateModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.ReadOnlyModelViewSet,
):
    search_fields = ["username", "email", "first_name", "last_name", "groups__name"]
    http_method_names = ["get", "post", "put", "delete", "head", "options", "trace"]
    suppress_write_response_data = True
    read_serializer_class = UserSerializer
    create_serializer_class = UserCreateSerializer
    update_serializer_class = UserUpdateSerializer
    permission_classes = [HasRolePermission]
    required_roles_by_action = {
        "create": ADMIN_ONLY_ROLES,
        "update": ADMIN_ONLY_ROLES,
        "destroy": ADMIN_ONLY_ROLES,
        "list": ADMIN_ONLY_ROLES,
        "retrieve": ADMIN_ONLY_ROLES,
    }

    def get_serializer_class(self):
        if self.action == "create":
            return self.create_serializer_class
        if self.action == "update":
            return self.update_serializer_class
        return self.read_serializer_class

    def get_queryset(self):
        return list_users_for_api()

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            user = UserService().create(data=serializer.validated_data)
        except DomainError as exc:
            return self.domain_error_response(exc)
        return Response(UserSerializer(user).data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        try:
            user = UserService().update(instance, data=serializer.validated_data)
        except DomainError as exc:
            return self.domain_error_response(exc)
        return Response(UserSerializer(user).data)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        UserService().soft_delete(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)
