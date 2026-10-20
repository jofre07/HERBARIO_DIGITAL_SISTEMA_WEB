from __future__ import annotations

from typing import Any, Protocol

from rest_framework import status, viewsets
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.serializers import Serializer

from apps.common.api.viewsets.mixins import DomainErrorResponseMixin, EncodedLookupMixin
from apps.common.exceptions import DomainError


class CRUDService(Protocol):
    def create(self, *, data: dict[str, Any]) -> Any: ...
    def update(self, instance: Any, *, data: dict[str, Any]) -> Any: ...
    def soft_delete(self, instance: Any) -> None: ...


class ServiceModelViewSet(EncodedLookupMixin, DomainErrorResponseMixin, viewsets.ModelViewSet):
    """ModelViewSet that delegates writes to a service class."""

    http_method_names = ["get", "post", "put", "delete", "head", "options", "trace"]
    suppress_write_response_data = True
    service_class: type[CRUDService]
    read_serializer_class: type[Serializer]
    write_serializer_class: type[Serializer]

    def get_service(self) -> CRUDService:
        return self.service_class()

    def get_serializer_class(self):
        if self.action in ("create", "update"):
            return self.write_serializer_class
        return self.read_serializer_class

    def create(self, request: Request, *args, **kwargs) -> Response:
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            instance = self.get_service().create(data=serializer.validated_data)
        except DomainError as exc:
            return self.domain_error_response(exc)
        return Response(
            self.read_serializer_class(instance).data,
            status=status.HTTP_201_CREATED,
        )

    def update(self, request: Request, *args, **kwargs) -> Response:
        partial = kwargs.pop("partial", False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        try:
            instance = self.get_service().update(instance, data=serializer.validated_data)
        except DomainError as exc:
            return self.domain_error_response(exc)
        return Response(self.read_serializer_class(instance).data)

    def perform_destroy(self, instance) -> None:
        self.get_service().soft_delete(instance)

    def destroy(self, request: Request, *args, **kwargs) -> Response:
        instance = self.get_object()
        try:
            self.get_service().soft_delete(instance)
        except DomainError as exc:
            return self.domain_error_response(exc)
        return Response(status=status.HTTP_204_NO_CONTENT)
