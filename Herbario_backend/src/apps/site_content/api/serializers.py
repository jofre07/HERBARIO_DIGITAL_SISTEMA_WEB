from __future__ import annotations

import json

from django.templatetags.static import static
from rest_framework import serializers

from apps.common.api.validators import validate_no_html
from apps.site_content.models import AboutPageContent


class AboutPageContentSerializer(serializers.ModelSerializer):
    introduction_image_url = serializers.SerializerMethodField()
    remove_introduction_image = serializers.BooleanField(write_only=True, required=False)

    class Meta:
        model = AboutPageContent
        fields = [
            "introduction_title",
            "introduction_body",
            "introduction_image",
            "introduction_image_url",
            "remove_introduction_image",
            "impact_items",
            "mission",
            "vision",
            "values",
            "team_title",
            "team_subtitle",
            "team_members",
            "contact_address",
            "contact_email",
            "contact_phone",
            "institution",
            "updated_at",
        ]
        read_only_fields = ["introduction_image_url", "updated_at"]
        extra_kwargs = {"introduction_image": {"write_only": True, "required": False}}

    def to_internal_value(self, data):
        mutable = dict(data.items()) if hasattr(data, "items") else data.copy()
        for field in ("impact_items", "values", "team_members"):
            value = mutable.get(field)
            if isinstance(value, str):
                try:
                    mutable[field] = json.loads(value)
                except json.JSONDecodeError:
                    raise serializers.ValidationError({field: "El formato enviado no es válido."})
        return super().to_internal_value(mutable)

    def validate(self, attrs):
        for field in (
            "introduction_title",
            "introduction_body",
            "mission",
            "vision",
            "team_title",
            "team_subtitle",
            "contact_address",
            "contact_phone",
            "institution",
        ):
            if field in attrs:
                validate_no_html(attrs[field])

        if "impact_items" in attrs:
            attrs["impact_items"] = self._validate_cards(attrs["impact_items"], "impact_items", 4)
        if "team_members" in attrs:
            attrs["team_members"] = self._validate_cards(attrs["team_members"], "team_members", 4)
        if "values" in attrs:
            values = attrs["values"]
            if not isinstance(values, list) or not 1 <= len(values) <= 10:
                raise serializers.ValidationError({"values": "Registra entre 1 y 10 valores."})
            for value in values:
                if not isinstance(value, str) or not value.strip():
                    raise serializers.ValidationError({"values": "Cada valor debe contener texto."})
                if len(value.strip()) > 120:
                    raise serializers.ValidationError({"values": "Cada valor admite hasta 120 caracteres."})
                validate_no_html(value)
            attrs["values"] = [value.strip() for value in values]
        return attrs

    def validate_introduction_image(self, image):
        if image.size > 10 * 1024 * 1024:
            raise serializers.ValidationError("La imagen no puede superar los 10 MB.")
        content_type = getattr(image, "content_type", "")
        if content_type and content_type not in {"image/jpeg", "image/png", "image/webp"}:
            raise serializers.ValidationError("Solo se permiten imágenes JPG, PNG o WebP.")
        return image

    def update(self, instance, validated_data):
        remove_image = validated_data.pop("remove_introduction_image", False)
        previous_image = instance.introduction_image.name if instance.introduction_image else ""
        instance = super().update(instance, validated_data)
        if remove_image and instance.introduction_image:
            instance.introduction_image.delete(save=False)
            instance.introduction_image = ""
            instance.save(update_fields=["introduction_image", "updated_at"])
        elif previous_image and "introduction_image" in validated_data:
            storage = instance.introduction_image.storage
            if previous_image != instance.introduction_image.name and storage.exists(previous_image):
                storage.delete(previous_image)
        return instance

    def get_introduction_image_url(self, obj: AboutPageContent) -> str | None:
        request = self.context.get("request")
        url = obj.introduction_image.url if obj.introduction_image else static("site_content/herbarium-about-default.png")
        return request.build_absolute_uri(url) if request else url

    def _validate_cards(self, value, field: str, expected: int) -> list[dict[str, str]]:
        if not isinstance(value, list) or len(value) != expected:
            raise serializers.ValidationError({field: f"Deben existir exactamente {expected} elementos."})
        cards = []
        for item in value:
            if not isinstance(item, dict):
                raise serializers.ValidationError({field: "Cada elemento debe ser un objeto."})
            title = str(item.get("title", "")).strip()
            description = str(item.get("description", "")).strip()
            if not title or not description:
                raise serializers.ValidationError({field: "Todos los títulos y descripciones son obligatorios."})
            if len(title) > 160 or len(description) > 500:
                raise serializers.ValidationError({field: "Los títulos admiten 160 caracteres y las descripciones 500."})
            validate_no_html(title)
            validate_no_html(description)
            cards.append({"title": title, "description": description})
        return cards
