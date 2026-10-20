from django.apps import AppConfig


class RolesConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.roles"

    def ready(self) -> None:
        from django.db.models.signals import post_migrate

        from apps.roles.seeders import seed_roles

        post_migrate.connect(
            seed_roles,
            dispatch_uid="apps.roles.seed_roles",
        )
