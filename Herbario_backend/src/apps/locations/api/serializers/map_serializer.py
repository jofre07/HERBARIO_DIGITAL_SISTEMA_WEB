from __future__ import annotations

from rest_framework import serializers

from apps.common.api.ids import EncodedPrimaryKeyRelatedField
from apps.media.services.image_variant_service import absolute_image_asset_url
from apps.specimens.models import Specimen, SpecimenLocation
from apps.taxonomy.models import Species


class MapPointSerializer(serializers.ModelSerializer):
    id = EncodedPrimaryKeyRelatedField(source="specimen", model=Specimen, read_only=True)
    species_id = EncodedPrimaryKeyRelatedField(
        source="specimen.species", model=Species, read_only=True
    )
    catalog_code = serializers.CharField(source="specimen.catalog_code", read_only=True)
    species_name = serializers.CharField(source="specimen.species.name", read_only=True)
    genus_name = serializers.CharField(source="specimen.species.genus.name", read_only=True)
    family_name = serializers.CharField(source="specimen.species.genus.family.name", read_only=True)
    common_names = serializers.SerializerMethodField()
    collector_name = serializers.CharField(source="specimen.collector.name", read_only=True)
    latitude = serializers.DecimalField(
        source="location.latitude", max_digits=10, decimal_places=8, read_only=True
    )
    longitude = serializers.DecimalField(
        source="location.longitude", max_digits=11, decimal_places=8, read_only=True
    )
    location_name = serializers.CharField(source="location.name", read_only=True)
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = SpecimenLocation
        fields = [
            "id",
            "catalog_code",
            "species_id",
            "species_name",
            "genus_name",
            "family_name",
            "common_names",
            "collector_name",
            "latitude",
            "longitude",
            "location_name",
            "image_url",
            "is_primary",
            "marker_icon",
        ]

    def get_image_url(self, obj: SpecimenLocation) -> str | None:
        image = obj.specimen.images.first()
        return absolute_image_asset_url(image, self.context.get("request")) if image else None

    def get_common_names(self, obj: SpecimenLocation) -> list[str]:
        return [common_name.common_name for common_name in obj.specimen.species.common_names.all()]
