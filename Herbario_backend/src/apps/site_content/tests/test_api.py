import json

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from rest_framework.test import APIClient

from apps.roles.repositories.membership_repository import replace_user_permissions


def test_public_about_content_is_available(db):
    response = APIClient().get("/api/public/content/about/")

    assert response.status_code == 200
    assert response.data["introduction_title"] == "¿Qué es el Herbario Digital?"
    assert len(response.data["impact_items"]) == 4
    assert response.data["introduction_image_url"].endswith(
        "/static/site_content/herbarium-about-default.png"
    )


def test_authorized_user_can_update_about_content(db):
    user = get_user_model().objects.create_user(username="content-editor", password="test-pass")
    permissions = Permission.objects.filter(
        content_type__app_label="site_content",
        codename__in=["view_aboutpagecontent", "change_aboutpagecontent"],
    )
    replace_user_permissions(user_id=user.pk, permission_ids=list(permissions.values_list("pk", flat=True)))
    client = APIClient()
    client.force_authenticate(user)

    response = client.patch(
        "/api/content/about/",
        {"introduction_title": "Un herbario para todos"},
        format="json",
    )

    assert response.status_code == 200
    assert response.data["introduction_title"] == "Un herbario para todos"


def test_authorized_user_can_update_json_fields_with_multipart_form(db):
    user = get_user_model().objects.create_user(username="multipart-editor", password="test-pass")
    permissions = Permission.objects.filter(
        content_type__app_label="site_content",
        codename__in=["view_aboutpagecontent", "change_aboutpagecontent"],
    )
    replace_user_permissions(user_id=user.pk, permission_ids=list(permissions.values_list("pk", flat=True)))
    client = APIClient()
    client.force_authenticate(user)
    impact_items = [
        {"title": f"Área {index}", "description": f"Descripción {index}"}
        for index in range(1, 5)
    ]

    response = client.patch(
        "/api/content/about/",
        {
            "impact_items": json.dumps(impact_items),
            "values": json.dumps(["Rigor", "Acceso abierto"]),
            "team_members": json.dumps(impact_items),
        },
        format="multipart",
    )

    assert response.status_code == 200
    assert response.data["impact_items"] == impact_items
    assert response.data["values"] == ["Rigor", "Acceso abierto"]
    assert response.data["team_members"] == impact_items


def test_user_without_permission_cannot_update_about_content(db):
    user = get_user_model().objects.create_user(username="viewer", password="test-pass")
    client = APIClient()
    client.force_authenticate(user)

    response = client.patch(
        "/api/content/about/",
        {"introduction_title": "Cambio no autorizado"},
        format="json",
    )

    assert response.status_code == 403
