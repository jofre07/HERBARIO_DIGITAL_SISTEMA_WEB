import pytest
from rest_framework.test import APIClient

from apps.common.models import SearchQuery
from apps.specimens.models import Specimen
from apps.taxonomy.models import Family, Genus, Species


def create_published_species(name: str, catalog_code: str) -> Species:
    family, _ = Family.objects.get_or_create(name="Familia búsquedas")
    genus, _ = Genus.objects.get_or_create(name="Género búsquedas", family=family)
    species = Species.objects.create(name=name, genus=genus)
    Specimen.objects.create(
        catalog_code=catalog_code,
        species=species,
        is_published=True,
    )
    return species


@pytest.mark.django_db
def test_public_searches_are_normalized_and_counted():
    create_published_species("Café arábigo", "SEARCH-001")
    client = APIClient()

    first = client.post("/api/public/searches/", {"term": "  Café   "}, format="json")
    second = client.post("/api/public/searches/", {"term": "café"}, format="json")

    assert first.status_code == 201
    assert second.status_code == 201
    query = SearchQuery.objects.get()
    assert query.term == "Café"
    assert query.normalized_term == "café"
    assert query.search_count == 2
    assert query.has_results is True


@pytest.mark.django_db
def test_filter_options_return_successful_searches_by_frequency():
    create_published_species("Café arábigo", "SEARCH-002")
    create_published_species("Anturio rojo", "SEARCH-003")
    client = APIClient()

    for _ in range(2):
        client.post("/api/public/searches/", {"term": "Anturio"}, format="json")
    for _ in range(3):
        client.post("/api/public/searches/", {"term": "Café"}, format="json")
    client.post("/api/public/searches/", {"term": "Sin resultados"}, format="json")

    response = client.get("/api/public/filter-options/")

    assert response.status_code == 200
    assert response.json()["data"]["popular_searches"] == ["Café", "Anturio"]
    assert SearchQuery.objects.get(normalized_term="sin resultados").search_count == 1


@pytest.mark.django_db
def test_public_search_rejects_blank_terms():
    response = APIClient().post(
        "/api/public/searches/",
        {"term": "   "},
        format="json",
    )

    assert response.status_code == 400
    assert SearchQuery.objects.count() == 0
