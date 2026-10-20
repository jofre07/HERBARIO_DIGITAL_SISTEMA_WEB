from __future__ import annotations

from rest_framework import serializers

from apps.common.services import normalize_search_term


class SearchQuerySerializer(serializers.Serializer):
    term = serializers.CharField(max_length=120, trim_whitespace=True)

    def validate_term(self, value: str) -> str:
        display_term, _ = normalize_search_term(value)
        if not display_term:
            raise serializers.ValidationError("Ingresa un término de búsqueda.")
        return display_term
