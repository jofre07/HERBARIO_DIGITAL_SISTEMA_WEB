from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from rest_framework.test import APIClient

from apps.common.api.ids import encode_external_id, model_namespace
from apps.roles.models import Role
from apps.roles.repositories.membership_repository import add_user_role


def _admin_client(db):
    user_model = get_user_model()
    admin = user_model.objects.create_user(username="roles-admin", password="secret123")
    role, _ = Role.objects.get_or_create(name="Administrador")
    add_user_role(user_id=admin.pk, role_id=role.pk)

    client = APIClient()
    client.force_authenticate(user=admin)
    return client


def test_roles_requires_admin(db):
    response = APIClient().get("/api/roles/")
    assert response.status_code == 401


def test_admin_can_create_role(db):
    client = _admin_client(db)

    response = client.post("/api/roles/", {"name": "Editor"}, format="json")

    assert response.status_code == 201
    assert response.data["name"] == "Editor"
    assert Role.objects.filter(name="Editor").exists() is True


def test_roles_list_accepts_page_size(db):
    client = _admin_client(db)
    Role.objects.get_or_create(name="Curador")
    Role.objects.get_or_create(name="Digitador")
    Role.objects.get_or_create(name="Investigador")

    response = client.get("/api/roles/?page_size=2")

    assert response.status_code == 200
    assert len(response.data["results"]) == 2


def test_admin_can_update_role(db):
    client = _admin_client(db)
    role = Role.objects.create(name="Temporal")
    role_id = encode_external_id(role.id, namespace=model_namespace(Role))

    response = client.put(f"/api/roles/{role_id}/", {"name": "Revisor"}, format="json")

    assert response.status_code == 200
    role.refresh_from_db()
    assert role.name == "Revisor"


def test_admin_delete_removes_role(db):
    client = _admin_client(db)
    role = Role.objects.create(name="Archivador")
    role_id = encode_external_id(role.id, namespace=model_namespace(Role))

    response = client.delete(f"/api/roles/{role_id}/")

    assert response.status_code == 204
    from django.db import connection
    with connection.cursor() as cursor:
        cursor.execute("SELECT deleted FROM auth_group WHERE id=%s", [role.pk])
        row = cursor.fetchone()
    assert row is not None
    assert bool(row[0]) is True


def test_role_detail_schema_accepts_encoded_id(db):
    response = APIClient().get("/api/schema/?format=json")

    assert response.status_code == 200
    parameter = response.data["paths"]["/api/roles/{id}/"]["get"]["parameters"][0]
    assert parameter["name"] == "id"
    assert parameter["schema"]["type"] == "string"
    assert parameter["schema"]["pattern"] == "^eid_[0-9a-zA-Z]+_[0-9a-zA-Z]+$"


def test_permissions_catalog_excludes_framework_permissions(db):
    client = _admin_client(db)
    technical_content_type, _ = ContentType.objects.get_or_create(
        app_label="token_blacklist",
        model="blacklistedtoken",
    )
    technical_permission, _ = Permission.objects.get_or_create(
        content_type=technical_content_type,
        codename="view_blacklistedtoken",
        defaults={"name": "Can view blacklisted token"},
    )
    business_permission = Permission.objects.get(
        content_type__app_label="specimens",
        codename="view_specimen",
    )

    response = client.get("/api/roles/permissions/")

    assert response.status_code == 200
    returned_ids = {item["id"] for item in response.data}
    assert encode_external_id(
        business_permission.id,
        namespace=model_namespace(Permission),
    ) in returned_ids
    assert encode_external_id(
        technical_permission.id,
        namespace=model_namespace(Permission),
    ) not in returned_ids


def test_role_rejects_framework_permission_assignment(db):
    client = _admin_client(db)
    technical_content_type, _ = ContentType.objects.get_or_create(
        app_label="token_blacklist",
        model="blacklistedtoken",
    )
    technical_permission, _ = Permission.objects.get_or_create(
        content_type=technical_content_type,
        codename="delete_blacklistedtoken",
        defaults={"name": "Can delete blacklisted token"},
    )
    technical_permission_id = encode_external_id(
        technical_permission.id,
        namespace=model_namespace(Permission),
    )

    response = client.post(
        "/api/roles/",
        {"name": "Rol Tecnico", "permission_ids": [technical_permission_id]},
        format="json",
    )

    assert response.status_code == 400
