import pytest
from django.test import Client
from rest_framework import status

from apps.common.api.responses import response_message
from apps.locations.models import Location
from apps.specimens.models import Specimen, SpecimenLocation
from apps.taxonomy.models import ConservationStatus, Family, Genus, Species, Status


def test_health_check_returns_ok():
    response = Client().get("/api/health/")
    assert response.status_code == 200
    data = response.json()
    assert data["code"] == 200
    assert data["message"] == "Proceso realizado exitosamente"
    assert data["data"]["status"] == "ok"


@pytest.mark.django_db
def test_stats_returns_ok():
    response = Client().get("/api/public/stats/")
    assert response.status_code == 200
    data = response.json()
    assert data["code"] == 200
    assert data["message"] == "Proceso realizado exitosamente"
    assert "species" in data["data"]
    assert "specimens" in data["data"]
    assert "collections" in data["data"]
    assert "charts" in data["data"]


@pytest.mark.django_db
def test_stats_returns_dashboard_chart_data():
    family = Family.objects.create(name="Orchidaceae")
    genus = Genus.objects.create(name="Epidendrum", family=family)
    species = Species.objects.create(name="Epidendrum nocturnum", genus=genus)
    location = Location.objects.create(
        name="Reserva",
        latitude=-0.180653,
        longitude=-78.467834,
    )
    specimen = Specimen.objects.create(
        catalog_code="SP-DASH-1",
        species=species,
        is_published=True,
        collection_date="2024-06-15",
    )
    SpecimenLocation.objects.create(specimen=specimen, location=location, is_primary=True)
    status_entry = Status.objects.get(code="EN")
    ConservationStatus.objects.create(species=species, status=status_entry)

    response = Client().get("/api/public/stats/")

    assert response.status_code == 200
    dashboard = response.json()["data"]
    assert dashboard["locations"] == 1
    assert dashboard["charts"]["specimens_by_family"] == [{"label": "Orchidaceae", "value": 1}]
    assert dashboard["charts"]["specimens_by_year"] == [{"label": "2024", "value": 1}]
    assert dashboard["charts"]["species_by_conservation_status"] == [{"label": "EN", "value": 1}]


@pytest.mark.django_db
def test_public_filter_options_are_compact_and_unpaginated():
    family = Family.objects.create(name="Lauraceae options")
    genus = Genus.objects.create(name="Ocotea options", family=family)
    species = Species.objects.create(name="insularis options", genus=genus)
    location = Location.objects.create(
        name="Pacoche options",
        latitude="-1.06000000",
        longitude="-80.88000000",
    )
    specimen = Specimen.objects.create(
        catalog_code="SP-OPTIONS", species=species, is_published=True
    )
    SpecimenLocation.objects.create(
        specimen=specimen,
        location=location,
        habitat="Bosque seco options",
        climate="Tropical options",
        is_primary=True,
    )
    duplicate_specimen = Specimen.objects.create(
        catalog_code="SP-OPTIONS-2", species=species, is_published=True
    )
    SpecimenLocation.objects.create(
        specimen=duplicate_specimen,
        location=location,
        habitat="Bosque seco options",
        climate="Tropical options",
        is_primary=True,
    )

    response = Client().get("/api/public/filter-options/")

    assert response.status_code == 200
    options = response.json()["data"]
    assert "Lauraceae options" in options["families"]
    assert {"name": "Ocotea options", "family_name": "Lauraceae options"} in options["genera"]
    assert "Pacoche options" in options["locations"]
    assert "Bosque seco options" in options["habitats"]
    assert "Tropical options" in options["climates"]
    assert options["habitats"].count("Bosque seco options") == 1
    assert options["climates"].count("Tropical options") == 1


@pytest.mark.parametrize(
    ("status_code", "message"),
    [
        (status.HTTP_201_CREATED, "Creado exitosamente"),
        (status.HTTP_200_OK, "Proceso realizado exitosamente"),
        (status.HTTP_204_NO_CONTENT, "Proceso realizado exitosamente"),
        (status.HTTP_400_BAD_REQUEST, "Has realizado una peticion incorrecta."),
        (status.HTTP_401_UNAUTHORIZED, "Usuario no autorizado."),
        (status.HTTP_403_FORBIDDEN, "No tienes permisos para realizar esta accion."),
        (status.HTTP_404_NOT_FOUND, "El recurso que has intentado solicitar no existe."),
        (
            status.HTTP_405_METHOD_NOT_ALLOWED,
            "Este metodo HTTP no esta permitido en el servidor.",
        ),
        (
            status.HTTP_409_CONFLICT,
            "El recurso que intentas crear o actualizar ya existe.",
        ),
        (
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            "Error en el servidor. No eres tu, soy yo. Comunicate con el administrador.",
        ),
    ],
)
def test_response_message_by_status_code(status_code, message):
    assert response_message(status_code) == message


def test_response_message_fallback():
    assert response_message(418) == "Error, Comunicate con el administrador."
