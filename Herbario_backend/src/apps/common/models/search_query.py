from __future__ import annotations

from django.db import models
from django.utils import timezone

from apps.common.models.base import TimeStampedModel


class SearchQuery(TimeStampedModel):
    term = models.CharField(max_length=120)
    normalized_term = models.CharField(max_length=120, unique=True)
    search_count = models.PositiveBigIntegerField(default=1)
    has_results = models.BooleanField(default=False, db_index=True)
    last_searched_at = models.DateTimeField(default=timezone.now, db_index=True)

    class Meta:
        db_table = "common_search_query"
        indexes = [
            models.Index(
                fields=["has_results", "-search_count", "-last_searched_at"],
                name="common_search_popular_idx",
            )
        ]

    def __str__(self) -> str:
        return f"{self.term} ({self.search_count})"
