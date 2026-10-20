from __future__ import annotations

from django.contrib.auth.models import Permission

from apps.roles.models import Role
from apps.roles.repositories.membership_repository import role_has_permission
from apps.roles.roles import ROLE_ADMIN, ROLE_CURATOR, ROLE_DIGITIZER, ROLE_RESEARCHER
from apps.roles.seeders import seed_roles


def test_seed_roles_assigns_permissions_by_role(db):
    seed_roles(using="default", verbosity=0)

    admin = Role.objects.get(name=ROLE_ADMIN)
    curator = Role.objects.get(name=ROLE_CURATOR)
    digitizer = Role.objects.get(name=ROLE_DIGITIZER)
    researcher = Role.objects.get(name=ROLE_RESEARCHER)

    delete_user = Permission.objects.get(codename="delete_user")
    change_species = Permission.objects.get(codename="change_species")
    delete_species = Permission.objects.get(codename="delete_species")
    add_specimen = Permission.objects.get(codename="add_specimen")
    add_species = Permission.objects.get(codename="add_species")
    view_species = Permission.objects.get(codename="view_species")

    assert role_has_permission(role_id=admin.pk, permission_id=delete_user.pk) is True
    assert role_has_permission(role_id=curator.pk, permission_id=change_species.pk) is True
    assert role_has_permission(role_id=curator.pk, permission_id=delete_species.pk) is False
    assert role_has_permission(role_id=digitizer.pk, permission_id=add_specimen.pk) is True
    assert role_has_permission(role_id=digitizer.pk, permission_id=add_species.pk) is False
    assert role_has_permission(role_id=researcher.pk, permission_id=view_species.pk) is True
    assert role_has_permission(
        role_id=researcher.pk, permission_id=add_specimen.pk
    ) is False
    assert Permission.objects.count() > 0
