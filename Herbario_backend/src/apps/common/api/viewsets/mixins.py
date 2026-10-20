from __future__ import annotations

from rest_framework import status
from rest_framework.exceptions import NotFound
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response

from apps.common.api.ids import InvalidExternalID, decode_external_id, model_namespace
from apps.common.exceptions import ConflictError, DomainError, NotFoundError


class EncodedLookupMixin:
    lookup_value_regex = r"eid_[0-9a-zA-Z]+_[0-9a-zA-Z]+"

    def get_object(self):
        queryset = self.filter_queryset(self.get_queryset())
        lookup_url_kwarg = self.lookup_url_kwarg or self.lookup_field
        lookup_value = self.kwargs[lookup_url_kwarg]

        if self.lookup_field in {"pk", "id"}:
            try:
                lookup_value = decode_external_id(
                    lookup_value,
                    namespace=model_namespace(queryset.model),
                )
            except InvalidExternalID as exc:
                raise NotFound("El identificador proporcionado no es válido.") from exc

        obj = get_object_or_404(queryset, **{self.lookup_field: lookup_value})
        self.check_object_permissions(self.request, obj)
        return obj


class DomainErrorResponseMixin:
    def domain_error_response(self, exc: DomainError) -> Response:
        if isinstance(exc, NotFoundError):
            return Response({"detail": str(exc)}, status=status.HTTP_404_NOT_FOUND)
        if isinstance(exc, ConflictError):
            return Response({"detail": str(exc)}, status=status.HTTP_409_CONFLICT)
        return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)
