import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

from apps.common.api.ids import encode_external_id, model_namespace
from apps.locations.models import Location
from apps.media.models import HerbariumImage
from apps.specimens.models import Specimen, SpecimenLocation
from apps.taxonomy.models import (
    CommonName,
    ConservationStatus,
    Family,
    Genus,
    Language,
    Species,
    Status,
    Translation,
)


@pytest.mark.django_db
def test_list_families_returns_ok():
    client = APIClient()
    user = get_user_model().objects.create_user(username="tax", password="secret123")
    client.force_authenticate(user=user)
    response = client.get("/api/taxonomy/families/")
    assert response.status_code == 200


@pytest.mark.django_db
def test_family_list_searches_in_backend():
    Family.objects.create(name="Fabaceae")
    Family.objects.create(name="Asteraceae")

    client = APIClient()
    user = get_user_model().objects.create_user(username="tax-search", password="secret123")
    client.force_authenticate(user=user)

    response = client.get("/api/taxonomy/families/?search=faba")

    assert response.status_code == 200
    assert response.data["count"] == 1
    assert response.data["results"][0]["name"] == "Fabaceae"


@pytest.mark.django_db
def test_family_detail_uses_encoded_id():
    family = Family.objects.create(name="Fabaceae")
    encoded_id = encode_external_id(family.id, namespace=model_namespace(Family))

    client = APIClient()
    user = get_user_model().objects.create_user(username="tax-detail", password="secret123")
    client.force_authenticate(user=user)

    response = client.get(f"/api/taxonomy/families/{encoded_id}/")
    raw_response = client.get(f"/api/taxonomy/families/{family.id}/")

    assert response.status_code == 200
    assert response.data["id"] == encoded_id
    assert raw_response.status_code == 404


@pytest.mark.django_db
def test_create_translation_accepts_translated_name():
    family = Family.objects.create(name="Asteraceae")
    genus = Genus.objects.create(name="Achyrocline", family=family)
    species = Species.objects.create(name="satureioides", genus=genus)
    spanish = Language.objects.get(code="es")
    english = Language.objects.get(code="en")
    common_name = CommonName.objects.create(
        species=species,
        language=spanish,
        common_name="Marcela",
        dialect="Espanol andino",
        region="Costa",
    )
    encoded_common_name_id = encode_external_id(
        common_name.id,
        namespace=model_namespace(CommonName),
    )
    encoded_language_id = encode_external_id(english.id, namespace=model_namespace(Language))

    client = APIClient()
    user = get_user_model().objects.create_superuser(
        username="tax-admin",
        email="tax-admin@example.com",
        password="secret123",
    )
    client.force_authenticate(user=user)

    response = client.post(
        "/api/taxonomy/translations/",
        {
            "common_name_id": encoded_common_name_id,
            "language_id": encoded_language_id,
            "translated_name": "Cudweed",
        },
        format="json",
    )

    assert response.status_code == 201
    assert response.data["common_name"] == "Marcela"
    assert response.data["common_name_id"] == encoded_common_name_id
    assert response.data["language_id"] == encoded_language_id
    assert response.data["language_code"] == "en"
    assert response.data["translated_name"] == "Cudweed"
    assert Translation.objects.filter(
        common_name=common_name,
        language=english,
        translated_name="Cudweed",
    ).exists()


@pytest.mark.django_db
def test_common_name_assigns_coast_region_internally():
    family = Family.objects.create(name="Orchidaceae")
    genus = Genus.objects.create(name="Epidendrum", family=family)
    species = Species.objects.create(name="jamiesonis", genus=genus)
    language = Language.objects.get(code="es")
    user = get_user_model().objects.create_superuser(
        username="common-name-admin",
        email="common-name-admin@example.com",
        password="secret123",
    )
    client = APIClient()
    client.force_authenticate(user=user)

    response = client.post(
        "/api/taxonomy/common-names/",
        {
            "species_id": encode_external_id(
                species.id,
                namespace=model_namespace(Species),
            ),
            "language_id": encode_external_id(
                language.id,
                namespace=model_namespace(Language),
            ),
            "common_name": "Flor de prueba",
            "region": "Region inventada",
        },
        format="json",
    )

    assert response.status_code == 201
    assert CommonName.objects.get(common_name="Flor de prueba").region == "Costa"


@pytest.mark.django_db
def test_languages_are_read_only():
    client = APIClient()
    user = get_user_model().objects.create_superuser(
        username="language-admin",
        email="language-admin@example.com",
        password="secret123",
    )
    client.force_authenticate(user=user)

    list_response = client.get("/api/taxonomy/languages/?page_size=100")
    count_before = Language.objects.count()
    write_response = client.post(
        "/api/taxonomy/languages/",
        {"code": "qu", "name": "Quechua", "native_name": "Kichwa"},
        format="json",
    )

    assert list_response.status_code == 200
    assert {item["code"] for item in list_response.data["results"]} >= {"es", "en", "qu", "jiv"}
    assert write_response.status_code == 405
    assert Language.objects.count() == count_before


@pytest.mark.django_db
def test_create_status_returns_encoded_id_and_normalized_code():
    client = APIClient()
    user = get_user_model().objects.create_superuser(
        username="status-admin",
        email="status-admin@example.com",
        password="secret123",
    )
    client.force_authenticate(user=user)

    response = client.post(
        "/api/taxonomy/statuses/",
            {
                "code": "zz",
                "name": "Test status",
                "description": "Only used by API tests.",
            },
            format="json",
        )

    status = Status.objects.get(code="ZZ")
    assert response.status_code == 201
    assert response.data["id"] == encode_external_id(
        status.id,
        namespace=model_namespace(Status),
    )
    assert response.data["code"] == "ZZ"
    assert response.data["name"] == "Test status"
    rendered = response.json()
    assert rendered == {"code": 201, "message": "Creado exitosamente"}


@pytest.mark.django_db
def test_create_conservation_status_uses_status_catalog():
    family = Family.objects.create(name="Meliaceae")
    genus = Genus.objects.create(name="Cedrela", family=family)
    species = Species.objects.create(name="odorata", genus=genus)
    status = Status.objects.get(code="VU")
    encoded_species_id = encode_external_id(species.id, namespace=model_namespace(Species))
    encoded_status_id = encode_external_id(status.id, namespace=model_namespace(Status))

    client = APIClient()
    user = get_user_model().objects.create_superuser(
        username="conservation-admin",
        email="conservation-admin@example.com",
        password="secret123",
    )
    client.force_authenticate(user=user)

    response = client.post(
        "/api/taxonomy/conservation-statuses/",
        {
            "species_id": encoded_species_id,
            "status_id": encoded_status_id,
        },
        format="json",
    )

    assert response.status_code == 201
    assert response.data["species_id"] == encoded_species_id
    assert response.data["status_id"] == encoded_status_id
    assert response.data["status_code"] == "VU"
    assert response.data["status_name"] == "Vulnerable"
    assert ConservationStatus.objects.filter(species=species, status=status).exists()


@pytest.mark.django_db
def test_species_catalog_includes_specimen_location_environment_data():
    family = Family.objects.create(name="Catalog family")
    genus = Genus.objects.create(name="Catalog genus", family=family)
    species = Species.objects.create(name="Catalog species", genus=genus)
    specimen = Specimen.objects.create(
        catalog_code="CAT-001", species=species, is_published=True
    )
    location = Location.objects.create(
        name="Catalog location",
        latitude="-0.84214567",
        longitude="-80.16397842",
    )
    SpecimenLocation.objects.create(
        specimen=specimen,
        location=location,
        climate="Tropical húmedo",
        habitat="Bosque siempreverde",
        is_primary=True,
    )

    response = APIClient().get("/api/public/catalog/species/?q=Catalog species")

    assert response.status_code == 200
    item = response.json()["data"]["results"][0]
    assert item["specimen_count"] == 1
    assert item["location_names"] == ["Catalog location"]
    assert item["climates"] == ["Tropical húmedo"]
    assert item["habitats"] == ["Bosque siempreverde"]

    filtered = APIClient().get(
            "/api/public/catalog/species/",
        {
            "family_name": "catalog fam",
            "location_name": "catalog loc",
            "habitat": "siempreverde",
        },
    )
    assert filtered.status_code == 200
    assert filtered.data["count"] == 1


@pytest.mark.django_db
def test_species_catalog_can_filter_featured_species():
    family = Family.objects.create(name="Featured family")
    genus = Genus.objects.create(name="Featured genus", family=family)
    featured = Species.objects.create(
        name="Featured species",
        genus=genus,
        is_featured=True,
    )
    regular = Species.objects.create(name="Regular species", genus=genus)
    Specimen.objects.create(
        catalog_code="FEATURED-001",
        species=featured,
        is_published=True,
    )
    Specimen.objects.create(
        catalog_code="REGULAR-001",
        species=regular,
        is_published=True,
    )

    response = APIClient().get(
        "/api/public/catalog/species/",
        {"featured": "true"},
    )

    assert response.status_code == 200
    assert response.data["count"] == 1
    assert response.data["results"][0]["name"] == "Featured species"
    assert response.data["results"][0]["is_featured"] is True


@pytest.mark.django_db
def test_public_species_catalog_detail_includes_only_published_specimens():
    family = Family.objects.create(name="Detail family")
    genus = Genus.objects.create(name="Detail genus", family=family)
    species = Species.objects.create(name="Detail species", genus=genus)
    published = Specimen.objects.create(
        catalog_code="DETAIL-PUBLISHED",
        species=species,
        is_published=True,
    )
    private_specimen = Specimen.objects.create(
        catalog_code="DETAIL-PRIVATE",
        species=species,
        is_published=False,
    )
    species_id = encode_external_id(species.id, namespace=model_namespace(Species))

    public_images = [
        HerbariumImage.objects.create(
            specimen=published,
            url=f"https://example.com/public-detail-{index}.jpg",
            credit="Herbario",
        )
        for index in range(6)
    ]
    HerbariumImage.objects.create(
        specimen=private_specimen,
        url="https://example.com/private-detail.jpg",
    )

    response = APIClient().get(f"/api/public/catalog/species/{species_id}/")

    assert response.status_code == 200
    assert response.data["id"] == species_id
    assert response.data["name"] == "Detail species"
    assert "image_urls" not in response.data["specimens"][0]
    assert [item["catalog_code"] for item in response.data["specimens"]] == [
        published.catalog_code
    ]
    assert response.data["image_count"] == 6
    assert "image_url" not in response.data
    assert "images" not in response.data
    assert len(response.data["image_urls"]) == 5
    assert all(isinstance(url, str) for url in response.data["image_urls"])
    assert all("private-detail" not in url for url in response.data["image_urls"])

    images_response = APIClient().get(
        f"/api/public/catalog/species/{species_id}/images/",
        {"page": 2, "page_size": 5},
    )

    assert images_response.status_code == 200
    assert images_response.data["count"] == 6
    assert len(images_response.data["results"]) == 1
    assert images_response.data["next"] is None
    assert images_response.data["previous"] is not None
    assert images_response.data["results"][0]["url"] not in response.data["image_urls"]
    assert {item["id"] for item in images_response.data["results"]}.issubset({
        encode_external_id(image.id, namespace=model_namespace(HerbariumImage)) for image in public_images
    })


@pytest.mark.django_db
def test_public_species_catalog_detail_rejects_out_of_range_external_id():
    response = APIClient().get("/api/public/catalog/species/eid_INEXISTENTE_QA/")

    assert response.status_code == 404
    assert response.json()["errors"]["detail"] == "El identificador proporcionado no es válido."
