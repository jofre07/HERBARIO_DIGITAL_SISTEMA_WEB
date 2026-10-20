from django.apps import AppConfig


class UsersConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.users"

    def ready(self) -> None:
        from django.db.models.signals import post_migrate

        from apps.users.seeders import seed_initial_admin

        post_migrate.connect(
            seed_initial_admin,
            sender=self,
            dispatch_uid="apps.users.seed_initial_admin",
        )
