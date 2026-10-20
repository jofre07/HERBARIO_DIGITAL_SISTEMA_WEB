from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="SearchQuery",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True, db_index=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("term", models.CharField(max_length=120)),
                ("normalized_term", models.CharField(max_length=120, unique=True)),
                ("search_count", models.PositiveBigIntegerField(default=1)),
                ("has_results", models.BooleanField(db_index=True, default=False)),
                (
                    "last_searched_at",
                    models.DateTimeField(db_index=True, default=django.utils.timezone.now),
                ),
            ],
            options={
                "db_table": "common_search_query",
                "indexes": [
                    models.Index(
                        fields=["has_results", "-search_count", "-last_searched_at"],
                        name="common_search_popular_idx",
                    )
                ],
            },
        ),
    ]
