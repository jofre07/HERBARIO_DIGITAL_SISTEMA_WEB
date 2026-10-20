import django.db.models.deletion
from django.db import migrations, models


def normalize_location_environment(apps, schema_editor):
    Climate = apps.get_model("locations", "Climate")
    ClimateHabitat = apps.get_model("locations", "ClimateHabitat")
    Habitat = apps.get_model("locations", "Habitat")

    climates = {}
    habitats = {}
    for record in ClimateHabitat.objects.all().order_by("id"):
        climate_name = record.climate_text.strip()
        habitat_name = record.habitat_text.strip()
        if climate_name:
            key = climate_name.casefold()
            climate = climates.get(key)
            if climate is None:
                climate, _ = Climate.objects.get_or_create(name=climate_name)
                climates[key] = climate
            record.climate_id = climate.pk
        if habitat_name:
            key = habitat_name.casefold()
            habitat = habitats.get(key)
            if habitat is None:
                habitat, _ = Habitat.objects.get_or_create(name=habitat_name)
                habitats[key] = habitat
            record.habitat_id = habitat.pk
        record.save(update_fields=["climate", "habitat"])


class Migration(migrations.Migration):
    dependencies = [("locations", "0002_location_coordinate_precision")]

    operations = [
        migrations.RemoveIndex(
            model_name="climatehabitat",
            name="locations_c_deleted_19d23e_idx",
        ),
        migrations.RemoveIndex(
            model_name="climatehabitat",
            name="locations_c_habitat_a7d627_idx",
        ),
        migrations.RenameField(
            model_name="climatehabitat",
            old_name="climate",
            new_name="climate_text",
        ),
        migrations.RenameField(
            model_name="climatehabitat",
            old_name="habitat",
            new_name="habitat_text",
        ),
        migrations.CreateModel(
            name="Climate",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True, db_index=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("deleted", models.BooleanField(db_index=True, default=False)),
                ("deleted_at", models.DateTimeField(blank=True, null=True)),
                ("name", models.CharField(max_length=100, unique=True)),
            ],
            options={"db_table": "locations_climate", "ordering": ["name"]},
        ),
        migrations.CreateModel(
            name="Habitat",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True, db_index=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("deleted", models.BooleanField(db_index=True, default=False)),
                ("deleted_at", models.DateTimeField(blank=True, null=True)),
                ("name", models.CharField(max_length=100, unique=True)),
            ],
            options={"db_table": "locations_habitat", "ordering": ["name"]},
        ),
        migrations.AddField(
            model_name="climatehabitat",
            name="climate",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="location_links",
                to="locations.climate",
            ),
        ),
        migrations.AddField(
            model_name="climatehabitat",
            name="habitat",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="location_links",
                to="locations.habitat",
            ),
        ),
        migrations.RunPython(normalize_location_environment, migrations.RunPython.noop),
        migrations.RemoveField(model_name="climatehabitat", name="climate_text"),
        migrations.RemoveField(model_name="climatehabitat", name="habitat_text"),
        migrations.AddIndex(
            model_name="climatehabitat",
            index=models.Index(
                fields=["deleted", "climate"], name="locations_c_deleted_8d160e_idx"
            ),
        ),
        migrations.AddIndex(
            model_name="climatehabitat",
            index=models.Index(fields=["habitat"], name="locations_c_habitat_7d0360_idx"),
        ),
    ]
