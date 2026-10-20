from django.apps import AppConfig


class TaxonomyConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.taxonomy"

    def ready(self) -> None:
        from django.db.models.signals import post_migrate

        from apps.taxonomy.seeders import seed_languages, seed_statuses

        post_migrate.connect(
            seed_languages,
            sender=self,
            dispatch_uid="apps.taxonomy.seed_languages",
        )

        post_migrate.connect(
            seed_statuses,
            sender=self,
            dispatch_uid="apps.taxonomy.seed_statuses",
        )
