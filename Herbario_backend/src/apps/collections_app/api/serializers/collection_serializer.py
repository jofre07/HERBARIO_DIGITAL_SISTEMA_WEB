from __future__ import annotations

from rest_framework import serializers

from apps.collections_app.models import Collection
from apps.common.api.ids import EncodedIDField, EncodedPrimaryKeyRelatedField
from apps.common.api.validators import validate_letters_spaces, validate_no_html
from apps.media.services.image_variant_service import absolute_image_asset_url
from apps.specimens.models import Specimen


class CollectionSerializer(serializers.ModelSerializer):
    id = EncodedIDField()
    specimen_ids = EncodedPrimaryKeyRelatedField(
        source="specimens",
        model=Specimen,
        many=True,
        read_only=True,
    )
    collection_type_label = serializers.CharField(
        source="get_collection_type_display", read_only=True
    )
    specimen_count = serializers.SerializerMethodField()
    species_count = serializers.SerializerMethodField()
    location_count = serializers.SerializerMethodField()
    image_url = serializers.SerializerMethodField()
    family_names = serializers.SerializerMethodField()
    location_names = serializers.SerializerMethodField()
    conservation_statuses = serializers.SerializerMethodField()

    class Meta:
        model = Collection
        fields = [
            "id",
            "name",
            "description",
            "collection_type",
            "collection_type_label",
            "specimen_ids",
            "specimen_count",
            "species_count",
            "location_count",
            "image_url",
            "family_names",
            "location_names",
            "conservation_statuses",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

    def get_specimen_count(self, obj: Collection) -> int:
        return len(obj.specimens.all())

    def get_species_count(self, obj: Collection) -> int:
        return len({specimen.species_id for specimen in obj.specimens.all()})

    def get_location_count(self, obj: Collection) -> int:
        return len(
            {
                link.location_id
                for specimen in obj.specimens.all()
                for link in specimen.location_links.all()
            }
        )

    def get_image_url(self, obj: Collection) -> str | None:
        for specimen in obj.specimens.all():
            image = specimen.images.first()
            if image:
                return absolute_image_asset_url(image, self.context.get("request"))
        return None

    def get_family_names(self, obj: Collection) -> list[str]:
        return sorted(
            {specimen.species.genus.family.name for specimen in obj.specimens.all()}
        )

    def get_location_names(self, obj: Collection) -> list[str]:
        return sorted(
            {
                link.location.name
                for specimen in obj.specimens.all()
                for link in specimen.location_links.all()
            }
        )

    def get_conservation_statuses(self, obj: Collection) -> list[str]:
        return sorted(
            {
                record.status.name
                for specimen in obj.specimens.all()
                for record in specimen.species.conservation_statuses.all()
            }
        )


class CollectionWriteSerializer(serializers.ModelSerializer):
    specimen_ids = EncodedPrimaryKeyRelatedField(
        source="specimens",
        queryset=Specimen.objects.all(),
        many=True,
        required=False,
    )

    class Meta:
        model = Collection
        fields = ["name", "description", "collection_type", "specimen_ids"]

    def validate_name(self, value: str) -> str:
        validate_letters_spaces(value)
        return value

    def validate_description(self, value: str) -> str:
        validate_no_html(value)
        return value
