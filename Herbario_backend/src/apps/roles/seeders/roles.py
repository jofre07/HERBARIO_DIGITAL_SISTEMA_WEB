from __future__ import annotations

from django.contrib.auth.models import Permission
from django.db.models import Q

from apps.roles.models import Role
from apps.roles.permission_catalog import assignable_permissions
from apps.roles.repositories.membership_repository import replace_role_permissions
from apps.roles.roles import (
    ROLE_ADMIN,
    ROLE_CURATOR,
    ROLE_DIGITIZER,
    ROLE_PUBLIC,
    ROLE_RESEARCHER,
    SYSTEM_ROLE_NAMES,
)

DOMAIN_APP_LABELS = {
    "collections_app",
    "collectors",
    "locations",
    "media",
    "specimens",
    "site_content",
    "taxonomy",
}
DATA_ENTRY_APP_LABELS = {
    "collectors",
    "locations",
    "media",
    "specimens",
}
CURATOR_APP_LABELS = DOMAIN_APP_LABELS
ADMIN_APP_LABELS = DOMAIN_APP_LABELS | {"auth", "users"}

ROLE_PERMISSION_RULES = {
    ROLE_ADMIN: {
        "app_labels": ADMIN_APP_LABELS,
        "actions": {"add", "change", "delete", "view"},
    },
    ROLE_CURATOR: {
        "app_labels": CURATOR_APP_LABELS,
        "actions": {"add", "change", "view"},
    },
    ROLE_DIGITIZER: {
        "app_labels": DATA_ENTRY_APP_LABELS,
        "actions": {"add", "change", "view"},
        "extra_view_app_labels": DOMAIN_APP_LABELS,
    },
    ROLE_RESEARCHER: {
        "app_labels": DOMAIN_APP_LABELS,
        "actions": {"view"},
    },
    ROLE_PUBLIC: {
        "app_labels": DOMAIN_APP_LABELS,
        "actions": {"view"},
    },
}


def seed_roles(*, using: str, verbosity: int = 1, **kwargs) -> None:
    for name in SYSTEM_ROLE_NAMES:
        role, _ = Role.objects.db_manager(using).get_or_create(name=name)
        perm_ids = list(
            _permissions_for_role(name, using=using).values_list("pk", flat=True)
        )
        replace_role_permissions(role_id=role.pk, permission_ids=perm_ids)

    sender = kwargs.get("sender")
    should_print = sender is None or getattr(sender, "name", "") == "apps.collections_app"
    if verbosity >= 1 and should_print:
        print("Roles ensured.")


def _permissions_for_role(role_name: str, *, using: str):
    rule = ROLE_PERMISSION_RULES[role_name]
    app_labels = rule["app_labels"]
    actions = rule["actions"]
    action_filter = Q()
    for action in actions:
        action_filter |= Q(codename__startswith=f"{action}_")
    query = Permission.objects.db_manager(using).filter(
        action_filter,
        content_type__app_label__in=app_labels,
    )

    extra_view_app_labels = rule.get("extra_view_app_labels")
    if extra_view_app_labels:
        query = query | Permission.objects.db_manager(using).filter(
            content_type__app_label__in=extra_view_app_labels,
            codename__startswith="view_",
        )

    return assignable_permissions(query).distinct()
