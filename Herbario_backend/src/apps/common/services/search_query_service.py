from __future__ import annotations

from django.db import IntegrityError
from django.db.models import F
from django.utils import timezone

from apps.common.models import SearchQuery
from apps.taxonomy.selectors import list_species_catalog_for_api


def normalize_search_term(term: str) -> tuple[str, str]:
    display_term = " ".join(term.split())
    return display_term, display_term.casefold()


def record_search_query(term: str) -> SearchQuery:
    display_term, normalized_term = normalize_search_term(term)
    now = timezone.now()
    has_results = list_species_catalog_for_api({"q": display_term}).exists()
    update_values = {
        "search_count": F("search_count") + 1,
        "has_results": has_results,
        "last_searched_at": now,
        "updated_at": now,
    }

    updated = SearchQuery.objects.filter(normalized_term=normalized_term).update(**update_values)
    if not updated:
        try:
            return SearchQuery.objects.create(
                term=display_term,
                normalized_term=normalized_term,
                has_results=has_results,
                last_searched_at=now,
            )
        except IntegrityError:
            SearchQuery.objects.filter(normalized_term=normalized_term).update(**update_values)

    return SearchQuery.objects.get(normalized_term=normalized_term)
