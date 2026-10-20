from __future__ import annotations

from rest_framework import serializers

from apps.collectors.models import Collector
from apps.common.api.ids import EncodedIDField
from apps.common.api.validators import validate_letters_spaces, validate_no_html


class CollectorSerializer(serializers.ModelSerializer):
    id = EncodedIDField()

    class Meta:
        model = Collector
        fields = ["id", "name", "comment"]
        read_only_fields = ["id"]


class CollectorWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Collector
        fields = ["name", "comment"]

    def validate_name(self, value: str) -> str:
        validate_letters_spaces(value)
        return value

    def validate_comment(self, value: str) -> str:
        validate_no_html(value)
        return value
