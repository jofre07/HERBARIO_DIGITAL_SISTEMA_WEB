import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

from apps.collectors.models import Collector
from apps.locations.models import Location
from apps.specimens.models import Specimen, SpecimenLocation
from apps.taxonomy.models import CommonName, Family, Genus, Language, Species


@pytest.mark.django_db
def test_map_returns_all_specimen_points_without_global_pagination():
    user = get_user_model().objects.create_superuser(
        username="map-admin",
        email="map-admin@example.com",
        password="test-password",
    )
    family = Family.objects.create(name="Map family")
    genus = Genus.objects.create(name="Map genus", family=family)
    species = Species.objects.create(name="Map species", genus=genus)
    language = Language.objects.create(code="es-map", name="Español")
    CommonName.objects.create(species=species, language=language, common_name="Nombre mapa")
    collector = Collector.objects.create(name="Colector mapa")
    location = Location.objects.create(
        name="Map location",
        latitude=-0.180653,
        longitude=-78.467834,
    )
    specimens = Specimen.objects.bulk_create(
        [
            Specimen(
                catalog_code=f"SP-MAP-{index:02d}",
                species=species,
                collector=collector,
                is_published=True,
            )
            for index in range(25)
        ]
    )
    SpecimenLocation.objects.bulk_create(
        [
            SpecimenLocation(
                specimen=specimen,
                location=location,
                is_primary=True,
            )
            for specimen in specimens
        ]
    )
    client = APIClient()
    client.force_authenticate(user=user)

    response = client.get("/api/locations/map/points/")

    assert response.status_code == 200
    assert len(response.json()["data"]) == 25
    first_point = response.json()["data"][0]
    assert first_point["family_name"] == "Map family"
    assert first_point["genus_name"] == "Map genus"
    assert first_point["common_names"] == ["Nombre mapa"]
    assert first_point["collector_name"] == "Colector mapa"

    assert len(client.get("/api/locations/map/points/?common_name=nombre").json()["data"]) == 25
    collector_response = client.get("/api/locations/map/points/?collector_name=colector")
    assert len(collector_response.json()["data"]) == 25
    family_response = client.get("/api/locations/map/points/?family_name=map fam")
    assert len(family_response.json()["data"]) == 25
    species_response = client.get("/api/locations/map/points/?species_name=map spec")
    assert len(species_response.json()["data"]) == 25
    assert client.get("/api/locations/map/points/?common_name=inexistente").json()["data"] == []


@pytest.mark.django_db
def test_location_preserves_eight_decimal_places():
    location = Location.objects.create(
        name="Precise location",
        latitude="-0.84214567",
        longitude="-80.16397842",
    )

    location.refresh_from_db()

    assert str(location.latitude) == "-0.84214567"
    assert str(location.longitude) == "-80.16397842"
