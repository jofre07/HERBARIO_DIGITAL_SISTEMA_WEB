from django.contrib.auth import get_user_model
from django.test import override_settings

from apps.roles.repositories.membership_repository import get_user_role_names
from apps.roles.roles import ROLE_ADMIN
from apps.users.seeders import seed_initial_admin


@override_settings(
    INITIAL_ADMIN_USERNAME="seed-admin",
    INITIAL_ADMIN_EMAIL="seed-admin@example.com",
    INITIAL_ADMIN_PASSWORD="seed-secret123",
)
def test_seed_initial_admin_creates_regular_user_with_admin_role(db):
    seed_initial_admin(using="default", verbosity=0)
    seed_initial_admin(using="default", verbosity=0)

    user = get_user_model().objects.get(username="seed-admin")

    assert user.email == "seed-admin@example.com"
    assert user.is_active is True
    assert user.is_staff is False
    assert user.is_superuser is False
    assert user.check_password("seed-secret123") is True
    assert get_user_role_names(user_id=user.pk) == [ROLE_ADMIN]
