import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

from apps.common.api.ids import encode_external_id, model_namespace
from apps.locations.models import Climate, Habitat
from apps.roles.models import Role


@pytest.mark.django_db
def test_environment_catalogs_are_listed_separately():
    Climate.objects.create(name="Tropical húmedo")
    Habitat.objects.create(name="Bosque seco tropical")

    client = APIClient()
    climates = client.get("/api/public/locations/climates/")
    habitats = client.get("/api/public/locations/habitats/")

    assert climates.status_code == 200
    assert habitats.status_code == 200
    assert climates.data["results"][0]["name"] == "Tropical húmedo"
    assert habitats.data["results"][0]["name"] == "Bosque seco tropical"


@pytest.mark.django_db
def test_environment_catalog_rejects_case_insensitive_duplicates():
    Climate.objects.create(name="Tropical seco")
    user = get_user_model().objects.create_user(username="catalog-editor", password="secret123")
    role, _ = Role.objects.get_or_create(name="Digitador")
    user.groups.add(role)
    client = APIClient()
    client.force_authenticate(user=user)

    response = client.post(
        "/api/locations/climates/",
        {"name": "tropical seco"},
        format="json",
    )

    assert response.status_code == 400
    assert Climate.objects.filter(name__iexact="tropical seco").count() == 1


@pytest.mark.django_db
@pytest.mark.parametrize(
    ("endpoint", "model", "created_name", "updated_name"),
    [
        ("climates", Climate, "Clima de prueba", "Clima actualizado"),
        ("habitats", Habitat, "Bosque de prueba", "Bosque actualizado"),
    ],
)
def test_environment_catalog_crud(endpoint, model, created_name, updated_name):
    user = get_user_model().objects.create_superuser(
        username=f"{endpoint}-admin", password="secret123"
    )
    client = APIClient()
    client.force_authenticate(user=user)

    created = client.post(
        f"/api/locations/{endpoint}/", {"name": created_name}, format="json"
    )
    assert created.status_code == 201
    record = model.objects.get(name=created_name)
    encoded_id = encode_external_id(record.pk, namespace=model_namespace(model))

    updated = client.put(
        f"/api/locations/{endpoint}/{encoded_id}/",
        {"name": updated_name},
        format="json",
    )
    assert updated.status_code == 200
    record.refresh_from_db()
    assert record.name == updated_name

    deleted = client.delete(f"/api/locations/{endpoint}/{encoded_id}/")
    assert deleted.status_code == 204
    assert not model.objects.filter(pk=record.pk).exists()
