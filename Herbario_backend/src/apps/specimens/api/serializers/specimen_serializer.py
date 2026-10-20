from __future__ import annotations

from rest_framework import serializers

from apps.collectors.models import Collector
from apps.common.api.ids import (
    EncodedIDField,
    EncodedPrimaryKeyRelatedField,
    encode_external_id,
    model_namespace,
)
from apps.common.api.validators import (
    validate_alphanumeric_hyphen,
    validate_no_html,
)
from apps.locations.api.serializers.location_serializer import LocationWriteSerializer
from apps.locations.models import Climate, Habitat, Location
from apps.media.services.image_variant_service import image_asset_url
from apps.specimens.models import Specimen, SpecimenLocation
from apps.taxonomy.models import Species


class SpecimenNamedOptionSerializer(serializers.Serializer):
    id = serializers.SerializerMethodField()
    name = serializers.CharField(read_only=True)

    def get_id(self, obj) -> str:
        return encode_external_id(obj.pk, namespace=model_namespace(obj))


class SpecimenLocationOptionSerializer(serializers.ModelSerializer):
    id = EncodedIDField()

    class Meta:
        model = Location
        fields = ["id", "name", "latitude", "longitude", "comment"]


class SpecimenListSerializer(serializers.ModelSerializer):
    id = EncodedIDField()
    species_name = serializers.CharField(source="species.name", read_only=True)
    family_name = serializers.CharField(source="species.genus.family.name", read_only=True)
    genus_name = serializers.CharField(source="species.genus.name", read_only=True)
    collector_name = serializers.CharField(
        source="collector.name", read_only=True, allow_null=True
    )
    primary_location_name = serializers.SerializerMethodField()
    location_count = serializers.SerializerMethodField()

    class Meta:
        model = Specimen
        fields = [
            "id",
            "catalog_code",
            "species_name",
            "genus_name",
            "family_name",
            "collector_name",
            "primary_location_name",
            "location_count",
            "is_published",
        ]

    def _location_links(self, obj: Specimen) -> list[SpecimenLocation]:
        return list(obj.location_links.all())

    def get_primary_location_name(self, obj: Specimen) -> str | None:
        links = self._location_links(obj)
        primary = next((link for link in links if link.is_primary), links[0] if links else None)
        return primary.location.name if primary else None

    def get_location_count(self, obj: Specimen) -> int:
        return len(self._location_links(obj))


class SpecimenLocationSerializer(serializers.ModelSerializer):
    id = EncodedIDField()
    location_id = EncodedPrimaryKeyRelatedField(source="location", model=Location, read_only=True)
    location_name = serializers.CharField(source="location.name", read_only=True)
    latitude = serializers.DecimalField(
        source="location.latitude", max_digits=10, decimal_places=8, read_only=True
    )
    longitude = serializers.DecimalField(
        source="location.longitude", max_digits=11, decimal_places=8, read_only=True
    )
    location_comment = serializers.CharField(source="location.comment", read_only=True)
    climate_id = EncodedPrimaryKeyRelatedField(source="climate", model=Climate, read_only=True)
    climate_name = serializers.CharField(source="climate.name", read_only=True)
    habitat_id = EncodedPrimaryKeyRelatedField(source="habitat", model=Habitat, read_only=True)
    habitat_name = serializers.CharField(source="habitat.name", read_only=True)

    class Meta:
        model = SpecimenLocation
        fields = [
            "id",
            "location_id",
            "location_name",
            "latitude",
            "longitude",
            "location_comment",
            "climate_id",
            "climate_name",
            "habitat_id",
            "habitat_name",
            "comment",
            "marker_icon",
            "is_primary",
            "order",
        ]


class SpecimenLocationWriteSerializer(serializers.Serializer):
    location_id = EncodedPrimaryKeyRelatedField(
        source="location", queryset=Location.objects.all(), required=False
    )
    new_location = LocationWriteSerializer(required=False)
    climate_id = EncodedPrimaryKeyRelatedField(
        source="climate", queryset=Climate.objects.all(), allow_null=True, required=False
    )
    habitat_id = EncodedPrimaryKeyRelatedField(
        source="habitat", queryset=Habitat.objects.all(), allow_null=True, required=False
    )
    comment = serializers.CharField(allow_blank=True, required=False)
    marker_icon = serializers.ChoiceField(
        choices=SpecimenLocation.MARKER_ICON_CHOICES,
        default="plant",
    )
    is_primary = serializers.BooleanField(default=False)
    order = serializers.IntegerField(min_value=1, required=False)

    def validate(self, attrs: dict) -> dict:
        if ("location" in attrs) == ("new_location" in attrs):
            raise serializers.ValidationError(
                "Seleccione una ubicación existente o proporcione una ubicación nueva."
            )
        return attrs

    def validate_comment(self, value: str) -> str:
        validate_no_html(value)
        return value


class SpecimenSerializer(serializers.ModelSerializer):
    id = EncodedIDField()
    species_id = EncodedPrimaryKeyRelatedField(source="species", model=Species, read_only=True)
    collector_id = EncodedPrimaryKeyRelatedField(
        source="collector", model=Collector, read_only=True
    )
    species_name = serializers.CharField(source="species.name", read_only=True)
    family_name = serializers.CharField(source="species.genus.family.name", read_only=True)
    genus_name = serializers.CharField(source="species.genus.name", read_only=True)
    collector_name = serializers.CharField(source="collector.name", read_only=True)
    locations = SpecimenLocationSerializer(source="location_links", many=True, read_only=True)
    location_id = serializers.SerializerMethodField()
    latitude = serializers.SerializerMethodField()
    longitude = serializers.SerializerMethodField()
    conservation_status = serializers.SerializerMethodField()
    image_urls = serializers.SerializerMethodField()
    image_count = serializers.SerializerMethodField()

    class Meta:
        model = Specimen
        fields = [
            "id",
            "catalog_code",
            "is_published",
            "collection_date",
            "collection_number",
            "morphological_description",
            "species_id",
            "species_name",
            "genus_name",
            "family_name",
            "collector_id",
            "collector_name",
            "locations",
            "location_id",
            "latitude",
            "longitude",
            "conservation_status",
            "image_urls",
            "image_count",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

    def _primary_link(self, obj: Specimen) -> SpecimenLocation | None:
        links = list(obj.location_links.all())
        return next((link for link in links if link.is_primary), links[0] if links else None)

    def get_location_id(self, obj: Specimen) -> str | None:
        link = self._primary_link(obj)
        if link is None:
            return None
        return EncodedPrimaryKeyRelatedField(model=Location, read_only=True).to_representation(
            link.location
        )

    def get_latitude(self, obj: Specimen) -> str | None:
        link = self._primary_link(obj)
        return format(link.location.latitude, ".8f") if link else None

    def get_longitude(self, obj: Specimen) -> str | None:
        link = self._primary_link(obj)
        return format(link.location.longitude, ".8f") if link else None

    def get_conservation_status(self, obj: Specimen) -> str | None:
        record = obj.species.conservation_statuses.first()
        return record.status.name if record else None

    def get_image_urls(self, obj: Specimen) -> list[str]:
        request = self.context.get("request")
        urls: list[str] = []
        for image in obj.images.all():
            url = image_asset_url(image)
            if url:
                urls.append(
                    request.build_absolute_uri(url)
                    if request and url.startswith("/")
                    else url
                )
        return urls

    def get_image_count(self, obj: Specimen) -> int:
        return len(obj.images.all())


class AdminSpecimenSerializer(SpecimenSerializer):
    class Meta(SpecimenSerializer.Meta):
        fields = [
            field
            for field in SpecimenSerializer.Meta.fields
            if field not in {"image_urls", "image_count"}
        ]


class SpecimenWriteSerializer(serializers.ModelSerializer):
    species_id = EncodedPrimaryKeyRelatedField(source="species", queryset=Species.objects.all())
    collector_id = EncodedPrimaryKeyRelatedField(
        source="collector",
        queryset=Collector.objects.all(),
        allow_null=True,
        required=False,
    )
    locations = SpecimenLocationWriteSerializer(many=True, required=False)
    location_id = EncodedPrimaryKeyRelatedField(
        source="legacy_location",
        queryset=Location.objects.all(),
        allow_null=True,
        required=False,
        write_only=True,
    )

    class Meta:
        model = Specimen
        fields = [
            "catalog_code",
            "is_published",
            "collection_date",
            "collection_number",
            "morphological_description",
            "species_id",
            "collector_id",
            "locations",
            "location_id",
        ]

    def validate(self, attrs: dict) -> dict:
        legacy_location = attrs.pop("legacy_location", None)
        if "locations" not in attrs and legacy_location is not None:
            attrs["locations"] = [
                {
                    "location": legacy_location,
                    "is_primary": True,
                    "order": 1,
                }
            ]
        return attrs

    def validate_locations(self, value: list[dict]) -> list[dict]:
        location_ids = [item["location"].pk for item in value if "location" in item]
        if len(location_ids) != len(set(location_ids)):
            raise serializers.ValidationError("No se puede repetir una ubicación.")
        if value and sum(bool(item.get("is_primary")) for item in value) != 1:
            raise serializers.ValidationError("Debe existir exactamente una ubicación principal.")
        for index, item in enumerate(value, start=1):
            item.setdefault("order", index)
        return value

    def validate_catalog_code(self, value: str) -> str:
        validate_alphanumeric_hyphen(value)
        return value

    def validate_collection_number(self, value: str) -> str:
        validate_alphanumeric_hyphen(value)
        return value

    def validate_morphological_description(self, value: str) -> str:
        validate_no_html(value)
        return value
