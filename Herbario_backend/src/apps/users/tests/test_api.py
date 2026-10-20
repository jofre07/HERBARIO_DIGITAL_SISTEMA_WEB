from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

from apps.common.api.ids import encode_external_id, model_namespace
from apps.roles.models import Role
from apps.roles.repositories.membership_repository import (
    add_user_role,
    get_user_role_ids,
)


def test_users_requires_authentication():
    response = APIClient().get("/api/users/")
    assert response.status_code == 401


def test_users_list_for_authenticated_user(db):
    user_model = get_user_model()
    user = user_model.objects.create_user(username="api-admin", password="secret")
    user_model.objects.create_user(username="viewer", password="secret")
    role, _ = Role.objects.get_or_create(name="Administrador")
    add_user_role(user_id=user.pk, role_id=role.pk)

    client = APIClient()
    client.force_authenticate(user=user)
    response = client.get("/api/users/")
    assert response.status_code == 200


def test_admin_can_create_user_with_roles(db):
    user_model = get_user_model()
    admin = user_model.objects.create_user(username="admin-user", password="secret123")
    admin_role, _ = Role.objects.get_or_create(name="Administrador")
    target_role, _ = Role.objects.get_or_create(name="Investigador")
    add_user_role(user_id=admin.pk, role_id=admin_role.pk)

    client = APIClient()
    client.force_authenticate(user=admin)
    response = client.post(
        "/api/users/",
        {
            "username": "new-researcher",
            "email": "new-researcher@example.com",
            "password": "secret123",
            "role_ids": [
                encode_external_id(target_role.id, namespace=model_namespace(Role)),
            ],
        },
        format="json",
    )

    assert response.status_code == 201
    created_user = user_model.objects.get(username="new-researcher")
    assert created_user.check_password("secret123") is True
    assert target_role.pk in get_user_role_ids(user_id=created_user.pk)
    assert response.data["role_ids"] == [
        encode_external_id(target_role.id, namespace=model_namespace(Role)),
    ]
    assert response.data["roles"] == ["Investigador"]


def test_admin_can_put_user_and_replace_roles(db):
    user_model = get_user_model()
    admin = user_model.objects.create_user(username="admin-put-user", password="secret123")
    user = user_model.objects.create_user(username="editable-user", password="secret123")
    admin_role, _ = Role.objects.get_or_create(name="Administrador")
    researcher_role, _ = Role.objects.get_or_create(name="Investigador")
    curator_role, _ = Role.objects.get_or_create(name="Curador")
    add_user_role(user_id=admin.pk, role_id=admin_role.pk)
    add_user_role(user_id=user.pk, role_id=researcher_role.pk)

    client = APIClient()
    client.force_authenticate(user=admin)
    user_id = encode_external_id(user.id, namespace=model_namespace(user_model))
    response = client.put(
        f"/api/users/{user_id}/",
        {
            "username": "updated-user",
            "email": "updated-user@example.com",
            "is_active": True,
            "role_ids": [
                encode_external_id(curator_role.id, namespace=model_namespace(Role)),
            ],
        },
        format="json",
    )

    assert response.status_code == 200
    user.refresh_from_db()
    assert user.username == "updated-user"
    assert user.email == "updated-user@example.com"
    assert curator_role.pk in get_user_role_ids(user_id=user.pk)
    assert researcher_role.pk not in get_user_role_ids(user_id=user.pk)
    assert response.data["role_ids"] == [
        encode_external_id(curator_role.id, namespace=model_namespace(Role)),
    ]
    assert response.data["roles"] == ["Curador"]


def test_admin_can_patch_user_password(db):
    user_model = get_user_model()
    admin = user_model.objects.create_user(username="admin-patch-user", password="secret123")
    user = user_model.objects.create_user(username="patchable-user", password="secret123")
    role, _ = Role.objects.get_or_create(name="Administrador")
    add_user_role(user_id=admin.pk, role_id=role.pk)

    client = APIClient()
    client.force_authenticate(user=admin)
    user_id = encode_external_id(user.id, namespace=model_namespace(user_model))
    response = client.put(
        f"/api/users/{user_id}/",
        {"password": "new-secret123"},
        format="json",
    )

    assert response.status_code == 200
    user.refresh_from_db()
    assert user.check_password("new-secret123") is True


def test_admin_delete_deactivates_user(db):
    user_model = get_user_model()
    admin = user_model.objects.create_user(username="admin-delete-user", password="secret123")
    user = user_model.objects.create_user(username="deletable-user", password="secret123")
    role, _ = Role.objects.get_or_create(name="Administrador")
    add_user_role(user_id=admin.pk, role_id=role.pk)

    client = APIClient()
    client.force_authenticate(user=admin)
    user_id = encode_external_id(user.id, namespace=model_namespace(user_model))
    response = client.delete(f"/api/users/{user_id}/")

    assert response.status_code == 204
    user.refresh_from_db()
    assert user.is_active is False


def test_role_management_endpoints_are_not_publicly_registered(db):
    user_model = get_user_model()
    admin = user_model.objects.create_user(username="admin-hidden-routes", password="secret123")
    role, _ = Role.objects.get_or_create(name="Administrador")
    add_user_role(user_id=admin.pk, role_id=role.pk)

    client = APIClient()
    client.force_authenticate(user=admin)

    assert client.get("/api/users/roles/").status_code == 404
    assert client.get("/api/users/user-roles/").status_code == 404
    assert client.get("/api/users/logs/").status_code == 404


def test_login_response_includes_user_and_roles(db):
    user_model = get_user_model()
    user = user_model.objects.create_user(
        username="login-admin",
        email="login-admin@example.com",
        password="secret",
    )
    role, _ = Role.objects.get_or_create(name="Administrador")
    add_user_role(user_id=user.pk, role_id=role.pk)

    response = APIClient().post(
        "/api/token/",
        {"username": "login-admin", "password": "secret"},
        format="json",
    )

    assert response.status_code == 200
    assert "access" in response.data
    assert "refresh" in response.data
    assert response.data["user"] == {
        "id": encode_external_id(user.id, namespace=model_namespace(user_model)),
        "username": "login-admin",
        "email": "login-admin@example.com",
        "roles": ["Administrador"],
        "permissions": response.data["user"]["permissions"],
    }
    assert "auth.view_user" in response.data["user"]["permissions"]
    assert "specimens.add_specimen" in response.data["user"]["permissions"]


def test_login_invalid_credentials_returns_spanish_error(db):
    response = APIClient().post(
        "/api/token/",
        {"username": "missing-user", "password": "wrong-secret"},
        format="json",
    )

    assert response.status_code == 401
    assert response.json()["errors"]["detail"] == (
        "No existe una cuenta activa con las credenciales ingresadas."
    )


def test_refresh_rotates_and_blacklists_previous_token(db):
    get_user_model().objects.create_user(username="refresh-user", password="secret123")
    client = APIClient()
    login_response = client.post(
        "/api/token/",
        {"username": "refresh-user", "password": "secret123"},
        format="json",
    )
    previous_refresh = login_response.data["refresh"]

    refresh_response = client.post(
        "/api/token/refresh/",
        {"refresh": previous_refresh},
        format="json",
    )

    assert refresh_response.status_code == 200
    assert refresh_response.data["refresh"] != previous_refresh
    reused_response = client.post(
        "/api/token/refresh/",
        {"refresh": previous_refresh},
        format="json",
    )
    assert reused_response.status_code == 401
