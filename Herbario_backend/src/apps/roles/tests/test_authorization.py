import pytest
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from rest_framework.test import APIClient

from apps.roles.models import Role
from apps.roles.repositories.membership_repository import (
    add_user_role,
    replace_role_permissions,
)


@pytest.mark.django_db
def test_custom_role_is_authorized_by_assigned_permission():
    permission = Permission.objects.get(
        content_type__app_label="collectors",
        codename="add_collector",
    )
    role = Role.objects.create(name="Registrador de colectores")
    replace_role_permissions(role_id=role.pk, permission_ids=[permission.pk])

    user = get_user_model().objects.create_user(
        username="custom-collector-writer",
        password="secret123",
    )
    add_user_role(user_id=user.pk, role_id=role.pk)

    client = APIClient()
    client.force_authenticate(user=user)

    create_response = client.post(
        "/api/collectors/",
        {"name": "Ana Perez", "comment": "Registro de prueba"},
        format="json",
    )

    assert create_response.status_code == 201
    assert set(create_response.data) == {"id", "name", "comment"}
    assert "created_at" not in create_response.data
    assert "updated_at" not in create_response.data

    delete_response = client.delete(
        f"/api/collectors/{create_response.data['id']}/",
    )
    assert delete_response.status_code == 403
