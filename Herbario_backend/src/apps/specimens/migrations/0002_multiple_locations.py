import django.db.models.deletion
from django.db import migrations, models


def migrate_specimen_locations(apps, schema_editor):
    Specimen = apps.get_model("specimens", "Specimen")
    SpecimenLocation = apps.get_model("specimens", "SpecimenLocation")
    ClimateHabitat = apps.get_model("locations", "ClimateHabitat")

    climate_by_location = {}
    for record in ClimateHabitat.objects.filter(deleted=False).order_by("id"):
        climate_by_location.setdefault(record.location_id, record)

    links = []
    for specimen in Specimen.objects.exclude(location_id=None).iterator():
        environmental = climate_by_location.get(specimen.location_id)
        links.append(
            SpecimenLocation(
                specimen_id=specimen.id,
                location_id=specimen.location_id,
                climate=environmental.climate if environmental else "",
                habitat=environmental.habitat if environmental else "",
                is_primary=True,
                order=1,
            )
        )
    SpecimenLocation.objects.bulk_create(links)


def restore_primary_location(apps, schema_editor):
    Specimen = apps.get_model("specimens", "Specimen")
    SpecimenLocation = apps.get_model("specimens", "SpecimenLocation")
    for link in SpecimenLocation.objects.filter(is_primary=True).iterator():
        Specimen.objects.filter(pk=link.specimen_id).update(location_id=link.location_id)


class Migration(migrations.Migration):
    dependencies = [
        ("locations", "0002_location_coordinate_precision"),
        ("specimens", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="SpecimenLocation",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True, db_index=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("climate", models.CharField(blank=True, max_length=100)),
                ("habitat", models.CharField(blank=True, max_length=100)),
                ("comment", models.TextField(blank=True)),
                ("is_primary", models.BooleanField(default=False)),
                ("order", models.PositiveIntegerField(default=1)),
                (
                    "location",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="specimen_links",
                        to="locations.location",
                    ),
                ),
                (
                    "specimen",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="location_links",
                        to="specimens.specimen",
                    ),
                ),
            ],
            options={
                "db_table": "specimens_specimenlocation",
                "ordering": ["order", "id"],
                "indexes": [
                    models.Index(
                        fields=["specimen", "order"], name="specimens_s_specime_7b9ede_idx"
                    ),
                    models.Index(
                        fields=["location", "is_primary"], name="specimens_s_locatio_28ae77_idx"
                    ),
                ],
                "constraints": [
                    models.UniqueConstraint(
                        fields=("specimen", "location"), name="unique_specimen_location"
                    ),
                    models.UniqueConstraint(
                        condition=models.Q(("is_primary", True)),
                        fields=("specimen",),
                        name="unique_primary_location_per_specimen",
                    ),
                ],
            },
        ),
        migrations.AddField(
            model_name="specimen",
            name="locations",
            field=models.ManyToManyField(
                blank=True,
                related_name="specimens",
                through="specimens.SpecimenLocation",
                to="locations.location",
            ),
        ),
        migrations.RunPython(migrate_specimen_locations, restore_primary_location),
        migrations.RemoveField(model_name="specimen", name="location"),
    ]
