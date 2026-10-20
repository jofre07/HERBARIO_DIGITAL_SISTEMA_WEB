from __future__ import annotations

from apps.common.models import SearchQuery


def list_popular_search_terms(limit: int = 4) -> list[str]:
    return list(
        SearchQuery.objects.filter(has_results=True)
        .order_by("-search_count", "-last_searched_at", "term")
        .values_list("term", flat=True)[:limit]
    )
