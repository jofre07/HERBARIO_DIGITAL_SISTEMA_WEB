import pytest
from rest_framework.test import APIClient


@pytest.mark.django_db
@pytest.mark.parametrize(
    ("private_url", "public_url"),
    [
        ("/api/specimens/", "/api/public/specimens/"),
        ("/api/collections/", "/api/public/collections/"),
        ("/api/media/", "/api/public/media/"),
        ("/api/taxonomy/species/", "/api/public/taxonomy/species/"),
        ("/api/taxonomy/families/", "/api/public/taxonomy/families/"),
        ("/api/collectors/", "/api/public/collectors/"),
        ("/api/locations/", "/api/public/locations/"),
        ("/api/locations/climates/", "/api/public/locations/climates/"),
        ("/api/locations/habitats/", "/api/public/locations/habitats/"),
    ],
)
def test_public_reads_are_separated_from_private_endpoints(private_url, public_url):
    client = APIClient()

    assert client.get(private_url).status_code in {401, 403}
    assert client.get(public_url).status_code == 200
    assert client.post(public_url, {}, format="json").status_code == 405


@pytest.mark.django_db
@pytest.mark.parametrize(
    ("private_url", "public_url"),
    [
        ("/api/stats/", "/api/public/stats/"),
        ("/api/filter-options/", "/api/public/filter-options/"),
        ("/api/locations/map/points/", "/api/public/map/points/"),
        ("/api/taxonomy/catalog/species/", "/api/public/catalog/species/"),
    ],
)
def test_public_read_views_have_private_counterparts(private_url, public_url):
    client = APIClient()

    assert client.get(private_url).status_code in {401, 403}
    assert client.get(public_url).status_code == 200
