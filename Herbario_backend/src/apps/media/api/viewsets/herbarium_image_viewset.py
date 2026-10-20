from __future__ import annotations

from django.db.models import Max, Prefetch, Q
from drf_spectacular.utils import extend_schema
from rest_framework.decorators import action
from rest_framework.exceptions import NotFound
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response

from apps.common.api.ids import (
    InvalidExternalID,
    decode_external_id,
    decode_query_id,
    model_namespace,
)
from apps.common.viewsets.service_viewset import ServiceModelViewSet
from apps.locations.models import Location
from apps.media.api.serializers import (
    AdminSpecimenImageDetailSerializer,
    AdminSpecimenImageListSerializer,
    AdminSpecimenOptionSerializer,
    HerbariumImageSerializer,
    HerbariumImageWriteSerializer,
)
from apps.media.selectors import list_media_for_api
from apps.media.services import HerbariumImageService
from apps.roles.permissions import HasRolePermission
from apps.roles.roles import ADMIN_ONLY_ROLES, DATA_ENTRY_WRITE_ROLES, READ_ROLES
from apps.specimens.models import Specimen
from apps.specimens.publication import request_can_include_unpublished
from apps.taxonomy.models import Family, Species


@extend_schema(tags=["Imagenes"])
class HerbariumImageViewSet(ServiceModelViewSet):
    search_fields = [
        "url",
        "credit",
        "specimen__catalog_code",
        "specimen__species__name",
        "specimen__location_links__location__name",
    ]
    service_class = HerbariumImageService
    read_serializer_class = HerbariumImageSerializer
    write_serializer_class = HerbariumImageWriteSerializer
    permission_classes = [IsAuthenticated, HasRolePermission]
    required_roles_by_action = {
        "list": READ_ROLES,
        "retrieve": READ_ROLES,
        "create": DATA_ENTRY_WRITE_ROLES,
        "update": DATA_ENTRY_WRITE_ROLES,
        "partial_update": DATA_ENTRY_WRITE_ROLES,
        "destroy": ADMIN_ONLY_ROLES,
        "specimen_images": READ_ROLES,
        "specimen_options": READ_ROLES,
    }
    required_permissions_by_action = {
        "specimen_images": "media.view_herbariumimage",
        "specimen_options": "media.view_herbariumimage",
    }

    def list(self, request: Request, *args, **kwargs) -> Response:
        visible_images = list_media_for_api(
            include_unpublished=self.can_include_unpublished(request)
        )
        image_queryset = self.filter_queryset(self.get_queryset())
        specimen_queryset = Specimen.objects.filter(
            pk__in=image_queryset.values("specimen_id")
        ).prefetch_related(
            Prefetch(
                "images",
                queryset=visible_images.order_by("-created_at"),
                to_attr="filtered_images",
            )
        )

        ordering = request.query_params.get("ordering", "newest")
        if ordering in {"newest", "oldest"}:
            specimen_queryset = specimen_queryset.annotate(
                latest_image_created_at=Max("images__created_at")
            ).order_by(
                "-latest_image_created_at" if ordering == "newest" else "latest_image_created_at"
            )
        elif ordering == "species":
            specimen_queryset = specimen_queryset.order_by("species__name", "catalog_code")
        else:
            specimen_queryset = specimen_queryset.order_by("catalog_code")

        page = self.paginate_queryset(specimen_queryset)
        serializer = AdminSpecimenImageListSerializer(
            page if page is not None else specimen_queryset,
            many=True,
            context=self.get_serializer_context(),
        )
        if page is not None:
            return self.get_paginated_response(serializer.data)
        return Response(serializer.data)

    @action(
        detail=False,
        methods=["get"],
        permission_classes=[IsAuthenticated, HasRolePermission],
        url_path=r"specimens/(?P<specimen_id>eid_[0-9a-zA-Z]+_[0-9a-zA-Z]+)",
    )
    def specimen_images(self, request: Request, specimen_id: str | None = None) -> Response:
        try:
            decoded_specimen_id = decode_external_id(
                specimen_id or "",
                namespace=model_namespace(Specimen),
            )
        except InvalidExternalID as exc:
            raise NotFound("El identificador proporcionado no es válido.") from exc

        visible_images = list_media_for_api(
            include_unpublished=self.can_include_unpublished(request)
        ).filter(specimen_id=decoded_specimen_id).order_by("-created_at")
        specimen = (
            Specimen.objects.filter(pk=decoded_specimen_id)
            .prefetch_related(
                Prefetch(
                    "images",
                    queryset=visible_images,
                    to_attr="filtered_images",
                )
            )
            .first()
        )
        if specimen is None or not specimen.filtered_images:
            raise NotFound("No se encontraron imágenes para el espécimen solicitado.")

        serializer = AdminSpecimenImageDetailSerializer(
            specimen,
            context=self.get_serializer_context(),
        )
        return Response(serializer.data)

    @action(
        detail=False,
        methods=["get"],
        permission_classes=[IsAuthenticated, HasRolePermission],
        url_path="specimen-options",
    )
    def specimen_options(self, request: Request) -> Response:
        specimens = Specimen.objects.order_by("catalog_code").only("id", "catalog_code")
        serializer = AdminSpecimenOptionSerializer(specimens, many=True)
        return Response(serializer.data)

    def get_queryset(self):
        qs = list_media_for_api(include_unpublished=self.can_include_unpublished(self.request))
        species = decode_query_id(self.request.query_params, "species_id", Species)
        family = decode_query_id(self.request.query_params, "family_id", Family)
        location = decode_query_id(self.request.query_params, "location_id", Location)
        specimen = decode_query_id(self.request.query_params, "specimen_id", Specimen)
        species = species or decode_query_id(self.request.query_params, "species", Species)
        family = family or decode_query_id(self.request.query_params, "family", Family)
        location = location or decode_query_id(self.request.query_params, "location", Location)
        if species:
            qs = qs.filter(specimen__species_id=species)
        if family:
            qs = qs.filter(specimen__species__genus__family_id=family)
        if location:
            qs = qs.filter(specimen__location_links__location_id=location)
        if specimen:
            qs = qs.filter(specimen=specimen)
        if family_name := self.request.query_params.get("family_name"):
            qs = qs.filter(specimen__species__genus__family__name__icontains=family_name)
        if genus_name := self.request.query_params.get("genus_name"):
            qs = qs.filter(specimen__species__genus__name__icontains=genus_name)
        if species_name := self.request.query_params.get("species_name"):
            qs = qs.filter(specimen__species__name__icontains=species_name)
        if location_name := self.request.query_params.get("location_name"):
            qs = qs.filter(specimen__location_links__location__name__icontains=location_name)
        if conservation := self.request.query_params.get("conservation_status"):
            qs = qs.filter(
                Q(specimen__species__conservation_statuses__status__code__icontains=conservation)
                | Q(specimen__species__conservation_statuses__status__name__icontains=conservation)
            )
        if date_from := self.request.query_params.get("collection_date_from"):
            qs = qs.filter(specimen__collection_date__gte=date_from)
        if date_to := self.request.query_params.get("collection_date_to"):
            qs = qs.filter(specimen__collection_date__lte=date_to)
        if image_type := self.request.query_params.get("image_type"):
            if image_type != "specimen":
                qs = qs.none()
        ordering = self.request.query_params.get("ordering", "-created_at")
        ordering_map = {
            "newest": "-created_at",
            "oldest": "created_at",
            "species": "specimen__species__name",
            "catalog": "specimen__catalog_code",
        }
        qs = qs.order_by(ordering_map.get(ordering, "-created_at"))
        return qs.distinct()

    def can_include_unpublished(self, request: Request) -> bool:
        return request_can_include_unpublished(request)
