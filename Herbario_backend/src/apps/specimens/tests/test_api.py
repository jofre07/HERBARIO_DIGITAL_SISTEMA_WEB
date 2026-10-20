import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

from apps.collectors.models import Collector
from apps.common.api.ids import encode_external_id, model_namespace
from apps.locations.models import Climate, Habitat, Location
from apps.media.models import HerbariumImage
from apps.roles.models import Role
from apps.specimens.models import Specimen, SpecimenLocation
from apps.taxonomy.models import Family, Genus, Species


@pytest.mark.django_db
def test_list_specimens_returns_ok():
    family = Family.objects.create(name="Fabaceae")
    genus = Genus.objects.create(name="Phaseolus", family=family)
    species = Species.objects.create(name="vulgaris", genus=genus)
    Specimen.objects.create(catalog_code="SP-001", species=species, is_published=True)

    client = APIClient()
    user = get_user_model().objects.create_user(username="spec", password="secret123")
    client.force_authenticate(user=user)
    response = client.get("/api/specimens/")
    assert response.status_code == 200
    item = response.data["results"][0]
    assert item["conservation_status"] is None
    assert "image_urls" not in item
    assert "image_count" not in item


@pytest.mark.django_db
def test_admin_summary_list_returns_only_table_fields():
    family = Family.objects.create(name="Summary family")
    genus = Genus.objects.create(name="Summary genus", family=family)
    species = Species.objects.create(name="Summary species", genus=genus)
    specimen = Specimen.objects.create(
        catalog_code="SP-SUMMARY", species=species, is_published=True
    )
    location = Location.objects.create(
        name="Summary location", latitude="-0.10000000", longitude="-80.10000000"
    )
    SpecimenLocation.objects.create(
        specimen=specimen, location=location, is_primary=True
    )
    client = APIClient()
    admin = get_user_model().objects.create_superuser(
        username="summary-admin", email="summary@example.com", password="secret123"
    )
    client.force_authenticate(user=admin)

    response = client.get(
        "/api/specimens/", {"view": "summary", "include_unpublished": "true"}
    )

    assert response.status_code == 200
    assert response.data["results"][0] == {
        "id": encode_external_id(specimen.id, namespace=model_namespace(Specimen)),
        "catalog_code": "SP-SUMMARY",
        "species_name": "Summary species",
        "genus_name": "Summary genus",
        "family_name": "Summary family",
        "collector_name": None,
        "primary_location_name": "Summary location",
        "location_count": 1,
        "is_published": True,
    }


@pytest.mark.django_db
def test_admin_specimen_form_options_are_compact():
    family = Family.objects.create(name="Options family")
    genus = Genus.objects.create(name="Options genus", family=family)
    species = Species.objects.create(name="Options species", genus=genus)
    collector = Collector.objects.create(name="Options collector")
    location = Location.objects.create(
        name="Options location",
        latitude="-0.20000000",
        longitude="-80.20000000",
        comment="Reference point",
    )
    climate = Climate.objects.create(name="Options climate")
    habitat = Habitat.objects.create(name="Options habitat")
    client = APIClient()
    admin = get_user_model().objects.create_superuser(
        username="options-admin", email="options@example.com", password="secret123"
    )
    client.force_authenticate(user=admin)

    response = client.get("/api/specimens/form-options/")

    assert response.status_code == 200
    assert response.data == {
        "species": [
            {
                "id": encode_external_id(species.id, namespace=model_namespace(Species)),
                "name": "Options species",
            }
        ],
        "collectors": [
            {
                "id": encode_external_id(collector.id, namespace=model_namespace(Collector)),
                "name": "Options collector",
            }
        ],
        "locations": [
            {
                "id": encode_external_id(location.id, namespace=model_namespace(Location)),
                "name": "Options location",
                "latitude": "-0.20000000",
                "longitude": "-80.20000000",
                "comment": "Reference point",
            }
        ],
        "climates": [
            {
                "id": encode_external_id(climate.id, namespace=model_namespace(Climate)),
                "name": "Options climate",
            }
        ],
        "habitats": [
            {
                "id": encode_external_id(habitat.id, namespace=model_namespace(Habitat)),
                "name": "Options habitat",
            }
        ],
    }


@pytest.mark.django_db
def test_public_specimen_returns_stored_image_urls():
    family = Family.objects.create(name="Image family")
    genus = Genus.objects.create(name="Image genus", family=family)
    species = Species.objects.create(name="Image species", genus=genus)
    specimen = Specimen.objects.create(
        catalog_code="SP-IMAGE-001", species=species, is_published=True
    )
    HerbariumImage.objects.create(specimen=specimen, image="specimens/test/image.jpg")

    response = APIClient().get("/api/public/specimens/")

    assert response.status_code == 200
    assert response.data["results"][0]["image_urls"] == [
        "http://testserver/media/specimens/test/image.jpg"
    ]


@pytest.mark.django_db
def test_specimen_list_searches_related_taxonomy_in_backend():
    family = Family.objects.create(name="Fagaceae")
    matching_genus = Genus.objects.create(name="Quercus", family=family)
    other_genus = Genus.objects.create(name="Fagus", family=family)
    matching_species = Species.objects.create(name="humilis", genus=matching_genus)
    other_species = Species.objects.create(name="grandifolia", genus=other_genus)
    Specimen.objects.create(
        catalog_code="SP-SEARCH-001", species=matching_species, is_published=True
    )
    Specimen.objects.create(catalog_code="SP-SEARCH-002", species=other_species, is_published=True)

    client = APIClient()
    user = get_user_model().objects.create_user(username="spec-search", password="secret123")
    client.force_authenticate(user=user)

    response = client.get("/api/specimens/?search=quercus")

    assert response.status_code == 200
    assert response.data["count"] == 1
    assert response.data["results"][0]["catalog_code"] == "SP-SEARCH-001"


@pytest.mark.django_db
def test_public_specimen_filters_use_structured_backend_parameters():
    family = Family.objects.create(name="Lauraceae")
    genus = Genus.objects.create(name="Ocotea", family=family)
    species = Species.objects.create(name="insularis", genus=genus)
    specimen = Specimen.objects.create(
        catalog_code="SP-FILTER-001",
        species=species,
        is_published=True,
        collection_date="2024-06-15",
    )
    location = Location.objects.create(
        name="Bosque de Pacoche", latitude="-1.06000000", longitude="-80.88000000"
    )
    climate = Climate.objects.create(name="Tropical")
    habitat = Habitat.objects.create(name="Bosque seco")
    SpecimenLocation.objects.create(
        specimen=specimen,
        location=location,
        habitat=habitat,
        climate=climate,
        is_primary=True,
    )

    client = APIClient()
    user = get_user_model().objects.create_user(username="structured", password="secret123")
    client.force_authenticate(user=user)
    params = {
        "family_name": "laura",
        "genus_name": "ocot",
        "species_name": "insula",
        "location_name": "pacoche",
        "habitat": "seco",
        "climate": "tropical",
        "collection_date_from": "2024-01-01",
        "collection_date_to": "2024-12-31",
    }

    list_response = client.get("/api/public/specimens/", params)
    advanced_response = client.get("/api/public/specimens/", params)

    assert list_response.status_code == 200
    assert list_response.data["count"] == 1
    assert advanced_response.status_code == 200
    assert advanced_response.data["count"] == 1


@pytest.mark.django_db
def test_create_specimen_uses_species_id_field():
    family = Family.objects.create(name="Asteraceae")
    genus = Genus.objects.create(name="Helianthus", family=family)
    species = Species.objects.create(name="annuus", genus=genus)

    user = get_user_model().objects.create_user(username="spec-create", password="secret123")
    role, _ = Role.objects.get_or_create(name="Digitador")
    user.groups.add(role)

    client = APIClient()
    client.force_authenticate(user=user)
    response = client.post(
        "/api/specimens/",
        {
            "catalog_code": "SP-ID-001",
            "morphological_description": "Capitulo amarillo",
            "species_id": encode_external_id(species.id, namespace=model_namespace(Species)),
        },
        format="json",
    )

    assert response.status_code == 201
    assert response.data["species_id"] == encode_external_id(
        species.id,
        namespace=model_namespace(Species),
    )
    assert "species" not in response.data


@pytest.mark.django_db
def test_draft_specimen_is_publicly_hidden_and_authorized_admin_can_include_it():
    family = Family.objects.create(name="Draft family")
    genus = Genus.objects.create(name="Draft genus", family=family)
    species = Species.objects.create(name="Draft species", genus=genus)
    Specimen.objects.create(catalog_code="SP-DRAFT-001", species=species)
    admin = get_user_model().objects.create_superuser(
        username="draft-admin", email="draft-admin@example.com", password="secret123"
    )

    anonymous_client = APIClient()
    public_response = anonymous_client.get("/api/public/specimens/")
    private_response = anonymous_client.get("/api/specimens/")
    public_write_response = anonymous_client.post("/api/public/specimens/", {}, format="json")
    admin_client = APIClient()
    admin_client.force_authenticate(user=admin)
    admin_response = admin_client.get("/api/specimens/", {"include_unpublished": "true"})

    assert public_response.status_code == 200
    assert public_response.data["count"] == 0
    assert private_response.status_code in {401, 403}
    assert public_write_response.status_code == 405
    assert admin_response.status_code == 200
    assert admin_response.data["count"] == 1
    assert admin_response.data["results"][0]["is_published"] is False


@pytest.mark.django_db
def test_create_specimen_with_multiple_locations():
    family = Family.objects.create(name="Orchidaceae")
    genus = Genus.objects.create(name="Epidendrum", family=family)
    species = Species.objects.create(name="radicans", genus=genus)
    first = Location.objects.create(
        name="First location", latitude="-0.84214567", longitude="-80.16397842"
    )
    second = Location.objects.create(
        name="Second location", latitude="-0.84214568", longitude="-80.16397843"
    )
    humid_climate = Climate.objects.create(name="Tropical humedo")
    dry_climate = Climate.objects.create(name="Tropical seco")
    forest_habitat = Habitat.objects.create(name="Bosque")
    trail_habitat = Habitat.objects.create(name="Sendero")
    user = get_user_model().objects.create_user(username="spec-multiple", password="secret123")
    role, _ = Role.objects.get_or_create(name="Digitador")
    user.groups.add(role)
    client = APIClient()
    client.force_authenticate(user=user)

    response = client.post(
        "/api/specimens/",
        {
            "catalog_code": "SP-MULTI-001",
            "species_id": encode_external_id(species.id, namespace=model_namespace(Species)),
            "locations": [
                {
                    "location_id": encode_external_id(
                        first.id, namespace=model_namespace(Location)
                    ),
                    "is_primary": True,
                    "order": 1,
                    "climate_id": encode_external_id(
                        humid_climate.id, namespace=model_namespace(Climate)
                    ),
                    "habitat_id": encode_external_id(
                        forest_habitat.id, namespace=model_namespace(Habitat)
                    ),
                },
                {
                    "location_id": encode_external_id(
                        second.id, namespace=model_namespace(Location)
                    ),
                    "is_primary": False,
                    "order": 2,
                    "climate_id": encode_external_id(
                        dry_climate.id, namespace=model_namespace(Climate)
                    ),
                    "habitat_id": encode_external_id(
                        trail_habitat.id, namespace=model_namespace(Habitat)
                    ),
                },
            ],
        },
        format="json",
    )

    assert response.status_code == 201
    assert len(response.data["locations"]) == 2
    assert response.data["location_id"] == encode_external_id(
        first.id, namespace=model_namespace(Location)
    )
    assert SpecimenLocation.objects.filter(specimen__catalog_code="SP-MULTI-001").count() == 2


@pytest.mark.django_db
def test_rejects_duplicate_or_multiple_primary_locations():
    family = Family.objects.create(name="Rubiaceae")
    genus = Genus.objects.create(name="Coffea", family=family)
    species = Species.objects.create(name="arabica", genus=genus)
    location = Location.objects.create(name="Farm", latitude="-0.1", longitude="-80.1")
    user = get_user_model().objects.create_user(username="spec-invalid", password="secret123")
    role, _ = Role.objects.get_or_create(name="Digitador")
    user.groups.add(role)
    client = APIClient()
    client.force_authenticate(user=user)
    location_id = encode_external_id(location.id, namespace=model_namespace(Location))

    response = client.post(
        "/api/specimens/",
        {
            "catalog_code": "SP-MULTI-INVALID",
            "species_id": encode_external_id(species.id, namespace=model_namespace(Species)),
            "locations": [
                {"location_id": location_id, "is_primary": True},
                {"location_id": location_id, "is_primary": False},
            ],
        },
        format="json",
    )

    assert response.status_code == 400
    assert Specimen.objects.filter(catalog_code="SP-MULTI-INVALID").exists() is False


@pytest.mark.django_db
def test_creates_new_locations_atomically_with_specimen():
    family = Family.objects.create(name="Araceae")
    genus = Genus.objects.create(name="Anthurium", family=family)
    species = Species.objects.create(name="andraeanum", genus=genus)
    user = get_user_model().objects.create_user(username="spec-nested", password="secret123")
    role, _ = Role.objects.get_or_create(name="Digitador")
    user.groups.add(role)
    client = APIClient()
    client.force_authenticate(user=user)
    climate = Climate.objects.create(name="Humedo")
    habitat = Habitat.objects.create(name="Bosque")

    response = client.post(
        "/api/specimens/",
        {
            "catalog_code": "SP-NESTED-001",
            "species_id": encode_external_id(species.id, namespace=model_namespace(Species)),
            "locations": [
                {
                    "new_location": {
                        "name": "Reserva Central",
                        "latitude": "-0.84214567",
                        "longitude": "-80.16397842",
                        "comment": "Punto GPS",
                    },
                    "is_primary": True,
                    "marker_icon": "tree",
                    "climate_id": encode_external_id(
                        climate.id, namespace=model_namespace(Climate)
                    ),
                    "habitat_id": encode_external_id(
                        habitat.id, namespace=model_namespace(Habitat)
                    ),
                }
            ],
        },
        format="json",
    )

    assert response.status_code == 201
    assert response.data["is_published"] is False
    assert response.data["locations"][0]["latitude"] == "-0.84214567"
    assert response.data["locations"][0]["longitude"] == "-80.16397842"
    assert response.data["locations"][0]["marker_icon"] == "tree"
    assert Location.objects.filter(name="Reserva Central").exists()
