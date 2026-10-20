from __future__ import annotations

from django.contrib.auth import get_user_model

User = get_user_model()


class UserRepository:
    def list_all(self):
        return User.objects.all().order_by("id")

    def get_by_id(self, user_id: int):
        return User.objects.filter(pk=user_id).first()

    def get_by_username(self, username: str):
        return User.objects.filter(username=username).first()

    def username_exists_except(self, *, username: str, user_id: int) -> bool:
        return User.objects.filter(username=username).exclude(pk=user_id).exists()

    def create_user(self, *, username: str, email: str = "", password: str, is_active: bool = True):
        return User.objects.create_user(
            username=username,
            email=email,
            password=password,
            is_active=is_active,
        )

    def save(self, user):
        user.save()
        return user
