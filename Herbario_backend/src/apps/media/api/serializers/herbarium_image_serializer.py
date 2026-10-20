from __future__ import annotations

from rest_framework import serializers

from apps.common.api.ids import EncodedIDField, EncodedPrimaryKeyRelatedField
from apps.common.api.validators import validate_no_html
from apps.media.models import HerbariumImage
from apps.media.services.image_variant_service import image_asset_url
from apps.specimens.models import Specimen
from apps.taxonomy.models import Species


class HerbariumImageSerializer(serializers.ModelSerializer):
    id = EncodedIDField()
    specimen_id = EncodedPrimaryKeyRelatedField(source="specimen", model=Specimen, read_only=True)
    species_id = EncodedPrimaryKeyRelatedField(
        source="specimen.species", model=Species, read_only=True
    )
    catalog_code = serializers.CharField(source="specimen.catalog_code", read_only=True)
    species_name = serializers.CharField(source="specimen.species.name", read_only=True)
    genus_name = serializers.CharField(source="specimen.species.genus.name", read_only=True)
    family_name = serializers.CharField(source="specimen.species.genus.family.name", read_only=True)
    collection_date = serializers.DateField(source="specimen.collection_date", read_only=True)
    location_names = serializers.SerializerMethodField()
    conservation_status = serializers.SerializerMethodField()
    image_type = serializers.SerializerMethodField()
    url = serializers.SerializerMethodField()
    original_url = serializers.SerializerMethodField()
    variants = serializers.SerializerMethodField()

    class Meta:
        model = HerbariumImage
        fields = [
            "id",
            "specimen_id",
            "species_id",
            "catalog_code",
            "species_name",
            "genus_name",
            "family_name",
            "collection_date",
            "location_names",
            "conservation_status",
            "image_type",
            "url",
            "original_url",
            "variants",
            "credit",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

    def get_location_names(self, obj: HerbariumImage) -> list[str]:
        return [link.location.name for link in obj.specimen.location_links.all()]

    def get_conservation_status(self, obj: HerbariumImage) -> str | None:
        record = obj.specimen.species.conservation_statuses.first()
        return record.status.name if record else None

    def get_image_type(self, obj: HerbariumImage) -> str:
        return "specimen"

    def get_url(self, obj: HerbariumImage) -> str:
        return self._absolute_url(image_asset_url(obj))

    def get_original_url(self, obj: HerbariumImage) -> str:
        url = obj.image.url if obj.image else obj.url
        return self._absolute_url(url)

    def get_variants(self, obj: HerbariumImage) -> dict[str, dict]:
        return {
            variant.variant: {
                "url": self._absolute_url(variant.file.url),
                "width": variant.width,
                "height": variant.height,
                "file_size": variant.file_size,
                "format": variant.format,
            }
            for variant in obj.variants.all()
        }

    def _absolute_url(self, url: str) -> str:
        request = self.context.get("request")
        return request.build_absolute_uri(url) if request and url.startswith("/") else url


class HerbariumImageListItemSerializer(serializers.ModelSerializer):
    id = EncodedIDField()
    url = serializers.SerializerMethodField()
    original_url = serializers.SerializerMethodField()
    variants = serializers.SerializerMethodField()

    class Meta:
        model = HerbariumImage
        fields = ["id", "url", "original_url", "variants", "credit"]

    def get_url(self, obj: HerbariumImage) -> str:
        return self._absolute_url(image_asset_url(obj))

    def get_original_url(self, obj: HerbariumImage) -> str:
        return self._absolute_url(obj.image.url if obj.image else obj.url)

    def get_variants(self, obj: HerbariumImage) -> dict[str, dict]:
        return {
            variant.variant: {
                "url": self._absolute_url(variant.file.url),
                "width": variant.width,
                "height": variant.height,
                "file_size": variant.file_size,
                "format": variant.format,
            }
            for variant in obj.variants.all()
        }

    def _absolute_url(self, url: str) -> str:
        request = self.context.get("request")
        return request.build_absolute_uri(url) if request and url.startswith("/") else url


class AdminImageCoverSerializer(serializers.ModelSerializer):
    id = EncodedIDField()
    thumbnail_url = serializers.SerializerMethodField()

    class Meta:
        model = HerbariumImage
        fields = ["id", "thumbnail_url", "credit"]

    def get_thumbnail_url(self, obj: HerbariumImage) -> str:
        return self._absolute_url(image_asset_url(obj, "thumbnail"))

    def _absolute_url(self, url: str) -> str:
        request = self.context.get("request")
        return request.build_absolute_uri(url) if request and url.startswith("/") else url


class AdminImageAssetSerializer(serializers.ModelSerializer):
    id = EncodedIDField()
    variants = serializers.SerializerMethodField()

    class Meta:
        model = HerbariumImage
        fields = ["id", "credit", "variants"]

    def get_variants(self, obj: HerbariumImage) -> dict[str, dict[str, str]]:
        return {
            variant: {"url": self._absolute_url(image_asset_url(obj, variant))}
            for variant in ("thumbnail", "large")
        }

    def _absolute_url(self, url: str) -> str:
        request = self.context.get("request")
        return request.build_absolute_uri(url) if request and url.startswith("/") else url


class AdminSpecimenImageListSerializer(serializers.ModelSerializer):
    specimen_id = EncodedIDField(source="id")
    image_count = serializers.SerializerMethodField()
    cover = serializers.SerializerMethodField()

    class Meta:
        model = Specimen
        fields = ["specimen_id", "catalog_code", "image_count", "cover"]

    def get_image_count(self, obj: Specimen) -> int:
        return len(obj.filtered_images)

    def get_cover(self, obj: Specimen) -> dict | None:
        if not obj.filtered_images:
            return None
        return AdminImageCoverSerializer(
            obj.filtered_images[0],
            context=self.context,
        ).data


class AdminSpecimenImageDetailSerializer(serializers.ModelSerializer):
    specimen_id = EncodedIDField(source="id")
    images = AdminImageAssetSerializer(source="filtered_images", many=True)

    class Meta:
        model = Specimen
        fields = ["specimen_id", "catalog_code", "images"]


class AdminSpecimenOptionSerializer(serializers.ModelSerializer):
    id = EncodedIDField()

    class Meta:
        model = Specimen
        fields = ["id", "catalog_code"]


class HerbariumImageWriteSerializer(serializers.ModelSerializer):
    specimen_id = EncodedPrimaryKeyRelatedField(source="specimen", queryset=Specimen.objects.all())

    class Meta:
        model = HerbariumImage
        fields = ["specimen_id", "image", "url", "credit"]
        extra_kwargs = {
            "image": {"required": False},
            "url": {"required": False},
        }

    def validate_image(self, value):
        if value.size > 10 * 1024 * 1024:
            raise serializers.ValidationError("La imagen no puede superar los 10 MB.")
        if value.content_type not in {"image/jpeg", "image/png", "image/webp"}:
            raise serializers.ValidationError("Solo se permiten imágenes JPG, PNG o WEBP.")
        return value

    def validate(self, attrs):
        if not self.instance and not attrs.get("image") and not attrs.get("url"):
            raise serializers.ValidationError({"image": "Debes seleccionar una imagen."})
        return attrs

    def validate_credit(self, value: str) -> str:
        validate_no_html(value)
        return value
