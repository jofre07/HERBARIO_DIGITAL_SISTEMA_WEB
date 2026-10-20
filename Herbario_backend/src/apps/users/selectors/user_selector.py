from __future__ import annotations

from django.contrib.auth import get_user_model
from django.db.models import QuerySet

User = get_user_model()


def list_users_for_api() -> QuerySet:
    return User.objects.prefetch_related("groups").order_by("id")


def get_user_by_id(user_id: int):
    return list_users_for_api().filter(pk=user_id).first()
