from __future__ import annotations

from django.conf import settings
from django.contrib.auth import get_user_model

from apps.roles.models import Role
from apps.roles.repositories.membership_repository import add_user_role
from apps.roles.roles import ROLE_ADMIN


def seed_initial_admin(*, using: str, verbosity: int = 1, **kwargs) -> None:
    User = get_user_model()
    user, created = User.objects.db_manager(using).get_or_create(
        username=settings.INITIAL_ADMIN_USERNAME,
        defaults={
            "email": settings.INITIAL_ADMIN_EMAIL,
            "is_active": True,
            "is_staff": False,
            "is_superuser": False,
        },
    )

    if created:
        if settings.INITIAL_ADMIN_PASSWORD:
            user.set_password(settings.INITIAL_ADMIN_PASSWORD)
        else:
            user.set_unusable_password()
        user.save(using=using, update_fields=["password"])

    role, _ = Role.objects.db_manager(using).get_or_create(name=ROLE_ADMIN)
    add_user_role(user_id=user.pk, role_id=role.pk)

    if verbosity >= 1:
        action = "created" if created else "ensured"
        print(f"Initial admin user '{user.username}' {action}.")
