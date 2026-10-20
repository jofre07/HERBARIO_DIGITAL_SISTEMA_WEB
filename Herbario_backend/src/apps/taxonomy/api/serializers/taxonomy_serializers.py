from __future__ import annotations

from rest_framework import serializers

from apps.common.api.ids import EncodedIDField, EncodedPrimaryKeyRelatedField
from apps.common.api.validators import (
    validate_alphanumeric_hyphen,
    validate_letters_spaces,
    validate_no_html,
)
from apps.media.services.image_variant_service import image_asset_url
from apps.specimens.api.serializers.specimen_serializer import SpecimenSerializer
from apps.taxonomy.models import (
    CommonName,
    ConservationStatus,
    Family,
    Genus,
    Language,
    Species,
    Status,
    Translation,
)


class FamilySerializer(serializers.ModelSerializer):
    id = EncodedIDField()

    class Meta:
        model = Family
        fields = ["id", "name", "comment", "created_at", "updated_at"]
        read_only_fields = ["id", "created_at", "updated_at"]


class FamilyWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Family
        fields = ["name", "comment"]

    def validate_name(self, value: str) -> str:
        validate_letters_spaces(value)
        return value

    def validate_comment(self, value: str) -> str:
        validate_no_html(value)
        return value


class GenusSerializer(serializers.ModelSerializer):
    id = EncodedIDField()
    family_id = EncodedPrimaryKeyRelatedField(source="family", model=Family, read_only=True)
    family_name = serializers.CharField(source="family.name", read_only=True)

    class Meta:
        model = Genus
        fields = ["id", "name", "family_id", "family_name", "comment", "created_at", "updated_at"]
        read_only_fields = ["id", "created_at", "updated_at"]


class GenusWriteSerializer(serializers.ModelSerializer):
    family_id = EncodedPrimaryKeyRelatedField(source="family", queryset=Family.objects.all())

    class Meta:
        model = Genus
        fields = ["name", "family_id", "comment"]

    def validate_name(self, value: str) -> str:
        validate_letters_spaces(value)
        return value

    def validate_comment(self, value: str) -> str:
        validate_no_html(value)
        return value


class SpeciesSerializer(serializers.ModelSerializer):
    id = EncodedIDField()
    genus_id = EncodedPrimaryKeyRelatedField(source="genus", model=Genus, read_only=True)
    genus_name = serializers.CharField(source="genus.name", read_only=True)
    family_name = serializers.CharField(source="genus.family.name", read_only=True)

    class Meta:
        model = Species
        fields = [
            "id",
            "name",
            "genus_id",
            "genus_name",
            "family_name",
            "comment",
            "is_featured",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class SpeciesWriteSerializer(serializers.ModelSerializer):
    genus_id = EncodedPrimaryKeyRelatedField(source="genus", queryset=Genus.objects.all())

    class Meta:
        model = Species
        fields = ["name", "genus_id", "comment", "is_featured"]

    def validate_name(self, value: str) -> str:
        validate_letters_spaces(value)
        return value

    def validate_comment(self, value: str) -> str:
        validate_no_html(value)
        return value


class SpeciesCatalogSerializer(serializers.ModelSerializer):
    id = EncodedIDField()
    genus_name = serializers.CharField(source="genus.name", read_only=True)
    family_name = serializers.CharField(source="genus.family.name", read_only=True)
    common_names = serializers.StringRelatedField(many=True, read_only=True)
    conservation_status = serializers.SerializerMethodField()
    image_url = serializers.SerializerMethodField()
    specimen_count = serializers.SerializerMethodField()
    location_names = serializers.SerializerMethodField()
    climates = serializers.SerializerMethodField()
    habitats = serializers.SerializerMethodField()

    class Meta:
        model = Species
        fields = [
            "id",
            "name",
            "genus_name",
            "family_name",
            "comment",
            "is_featured",
            "common_names",
            "conservation_status",
            "image_url",
            "specimen_count",
            "location_names",
            "climates",
            "habitats",
        ]

    def get_conservation_status(self, obj: Species) -> str | None:
        record = obj.conservation_statuses.first()
        return record.status.name if record else None

    def get_image_url(self, obj: Species) -> str | None:
        for specimen in obj.specimens.all():
            image = specimen.images.first()
            if image:
                url = image_asset_url(image)
                request = self.context.get("request")
                return request.build_absolute_uri(url) if request and url.startswith("/") else url
        return None

    def get_specimen_count(self, obj: Species) -> int:
        return len(obj.specimens.all())

    def get_location_names(self, obj: Species) -> list[str]:
        return sorted(
            {
                link.location.name
                for specimen in obj.specimens.all()
                for link in specimen.location_links.all()
            }
        )

    def get_climates(self, obj: Species) -> list[str]:
        return sorted(
            {
                link.climate.name
                for specimen in obj.specimens.all()
                for link in specimen.location_links.all()
                if link.climate
            }
        )

    def get_habitats(self, obj: Species) -> list[str]:
        return sorted(
            {
                link.habitat.name
                for specimen in obj.specimens.all()
                for link in specimen.location_links.all()
                if link.habitat
            }
        )


class PublicCatalogSpecimenSerializer(SpecimenSerializer):
    class Meta(SpecimenSerializer.Meta):
        fields = [field for field in SpecimenSerializer.Meta.fields if field != "image_urls"]


class SpeciesCatalogDetailSerializer(SpeciesCatalogSerializer):
    specimens = PublicCatalogSpecimenSerializer(many=True, read_only=True)
    image_urls = serializers.SerializerMethodField()
    image_count = serializers.SerializerMethodField()

    class Meta(SpeciesCatalogSerializer.Meta):
        fields = [
            *[field for field in SpeciesCatalogSerializer.Meta.fields if field != "image_url"],
            "image_count",
            "image_urls",
            "specimens",
        ]

    def _published_images(self, obj: Species) -> list:
        cached = getattr(obj, "_public_catalog_images_cache", None)
        if cached is not None:
            return cached
        images = sorted(
            (
                image
                for specimen in obj.specimens.all()
                for image in specimen.images.all()
            ),
            key=lambda image: image.created_at,
            reverse=True,
        )
        obj._public_catalog_images_cache = images
        return images

    def get_image_urls(self, obj: Species) -> list[str]:
        request = self.context.get("request")
        urls: list[str] = []
        for image in self._published_images(obj)[:5]:
            url = image_asset_url(image)
            if url:
                urls.append(
                    request.build_absolute_uri(url)
                    if request and url.startswith("/")
                    else url
                )
        return urls

    def get_image_count(self, obj: Species) -> int:
        return len(self._published_images(obj))


class StatusSerializer(serializers.ModelSerializer):
    id = EncodedIDField()

    class Meta:
        model = Status
        fields = ["id", "code", "name", "description", "created_at", "updated_at"]
        read_only_fields = ["id", "created_at", "updated_at"]


class StatusWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Status
        fields = ["code", "name", "description"]

    def validate_code(self, value: str) -> str:
        validate_alphanumeric_hyphen(value)
        return value

    def validate_name(self, value: str) -> str:
        validate_letters_spaces(value)
        return value

    def validate_description(self, value: str) -> str:
        validate_no_html(value)
        return value


class LanguageSerializer(serializers.ModelSerializer):
    id = EncodedIDField()

    class Meta:
        model = Language
        fields = ["id", "code", "name", "native_name", "created_at", "updated_at"]
        read_only_fields = ["id", "created_at", "updated_at"]


class LanguageWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Language
        fields = ["code", "name", "native_name"]

    def validate_code(self, value: str) -> str:
        validate_alphanumeric_hyphen(value)
        return value

    def validate_name(self, value: str) -> str:
        validate_letters_spaces(value)
        return value

    def validate_native_name(self, value: str) -> str:
        validate_letters_spaces(value)
        return value


class CommonNameSerializer(serializers.ModelSerializer):
    id = EncodedIDField()
    species_id = EncodedPrimaryKeyRelatedField(source="species", model=Species, read_only=True)
    language_id = EncodedPrimaryKeyRelatedField(
        source="language",
        model=Language,
        read_only=True,
    )
    language_code = serializers.CharField(source="language.code", read_only=True)
    language_name = serializers.CharField(source="language.name", read_only=True)

    class Meta:
        model = CommonName
        fields = [
            "id",
            "species_id",
            "language_id",
            "language_code",
            "language_name",
            "common_name",
            "dialect",
            "region",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class CommonNameWriteSerializer(serializers.ModelSerializer):
    species_id = EncodedPrimaryKeyRelatedField(source="species", queryset=Species.objects.all())
    language_id = EncodedPrimaryKeyRelatedField(
        source="language",
        queryset=Language.objects.all(),
    )

    class Meta:
        model = CommonName
        fields = ["species_id", "language_id", "common_name", "dialect"]

    def validate_common_name(self, value: str) -> str:
        validate_letters_spaces(value)
        return value

    def validate_dialect(self, value: str) -> str:
        validate_letters_spaces(value)
        return value


class TranslationSerializer(serializers.ModelSerializer):
    id = EncodedIDField()
    common_name = serializers.CharField(
        source="common_name.common_name",
        read_only=True,
    )
    common_name_id = EncodedPrimaryKeyRelatedField(
        source="common_name",
        model=CommonName,
        read_only=True,
    )
    language_id = EncodedPrimaryKeyRelatedField(
        source="language",
        model=Language,
        read_only=True,
    )
    language_code = serializers.CharField(source="language.code", read_only=True)
    language_name = serializers.CharField(source="language.name", read_only=True)

    class Meta:
        model = Translation
        fields = [
            "id",
            "common_name",
            "common_name_id",
            "language_id",
            "language_code",
            "language_name",
            "translated_name",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class TranslationWriteSerializer(serializers.ModelSerializer):
    common_name_id = EncodedPrimaryKeyRelatedField(
        source="common_name",
        queryset=CommonName.objects.all(),
    )
    language_id = EncodedPrimaryKeyRelatedField(
        source="language",
        queryset=Language.objects.all(),
    )

    class Meta:
        model = Translation
        fields = ["common_name_id", "language_id", "translated_name"]

    def validate_translated_name(self, value: str) -> str:
        validate_letters_spaces(value)
        return value


class ConservationStatusSerializer(serializers.ModelSerializer):
    id = EncodedIDField()
    species_id = EncodedPrimaryKeyRelatedField(source="species", model=Species, read_only=True)
    status_id = EncodedPrimaryKeyRelatedField(source="status", model=Status, read_only=True)
    status_code = serializers.CharField(source="status.code", read_only=True)
    status_name = serializers.CharField(source="status.name", read_only=True)

    class Meta:
        model = ConservationStatus
        fields = [
            "id",
            "species_id",
            "status_id",
            "status_code",
            "status_name",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class ConservationStatusWriteSerializer(serializers.ModelSerializer):
    species_id = EncodedPrimaryKeyRelatedField(source="species", queryset=Species.objects.all())
    status_id = EncodedPrimaryKeyRelatedField(source="status", queryset=Status.objects.all())

    class Meta:
        model = ConservationStatus
        fields = ["species_id", "status_id"]
