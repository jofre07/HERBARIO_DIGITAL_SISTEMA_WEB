from __future__ import annotations

from rest_framework import serializers

from apps.common.api.ids import EncodedIDField, EncodedPrimaryKeyRelatedField
from apps.common.api.validators import validate_letters_spaces, validate_no_html
from apps.locations.models import Climate, ClimateHabitat, Habitat, Location


class ClimateSerializer(serializers.ModelSerializer):
    id = EncodedIDField()

    class Meta:
        model = Climate
        fields = ["id", "name"]

    def validate_name(self, value: str) -> str:
        validate_letters_spaces(value)
        value = value.strip()
        matches = Climate.objects.filter(name__iexact=value)
        if self.instance:
            matches = matches.exclude(pk=self.instance.pk)
        if matches.exists():
            raise serializers.ValidationError("Ya existe un clima con este nombre.")
        return value


class HabitatSerializer(serializers.ModelSerializer):
    id = EncodedIDField()

    class Meta:
        model = Habitat
        fields = ["id", "name"]

    def validate_name(self, value: str) -> str:
        validate_letters_spaces(value)
        value = value.strip()
        matches = Habitat.objects.filter(name__iexact=value)
        if self.instance:
            matches = matches.exclude(pk=self.instance.pk)
        if matches.exists():
            raise serializers.ValidationError("Ya existe un hábitat con este nombre.")
        return value


class LocationSerializer(serializers.ModelSerializer):
    id = EncodedIDField()
    specimen_count = serializers.IntegerField(read_only=True, default=0)

    class Meta:
        model = Location
        fields = [
            "id",
            "name",
            "latitude",
            "longitude",
            "comment",
            "specimen_count",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class LocationWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Location
        fields = ["name", "latitude", "longitude", "comment"]

    def validate_name(self, value: str) -> str:
        validate_letters_spaces(value)
        return value

    def validate_comment(self, value: str) -> str:
        validate_no_html(value)
        return value


class ClimateHabitatSerializer(serializers.ModelSerializer):
    id = EncodedIDField()
    location_id = EncodedPrimaryKeyRelatedField(source="location", model=Location, read_only=True)
    climate_id = EncodedPrimaryKeyRelatedField(source="climate", model=Climate, read_only=True)
    climate_name = serializers.CharField(source="climate.name", read_only=True)
    habitat_id = EncodedPrimaryKeyRelatedField(source="habitat", model=Habitat, read_only=True)
    habitat_name = serializers.CharField(source="habitat.name", read_only=True)

    class Meta:
        model = ClimateHabitat
        fields = [
            "id",
            "location_id",
            "climate_id",
            "climate_name",
            "habitat_id",
            "habitat_name",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class ClimateHabitatWriteSerializer(serializers.ModelSerializer):
    location_id = EncodedPrimaryKeyRelatedField(source="location", queryset=Location.objects.all())
    climate_id = EncodedPrimaryKeyRelatedField(
        source="climate", queryset=Climate.objects.all(), allow_null=True, required=False
    )
    habitat_id = EncodedPrimaryKeyRelatedField(
        source="habitat", queryset=Habitat.objects.all(), allow_null=True, required=False
    )

    class Meta:
        model = ClimateHabitat
        fields = ["location_id", "climate_id", "habitat_id"]
