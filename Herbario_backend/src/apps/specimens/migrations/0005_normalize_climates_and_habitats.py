import django.db.models.deletion
from django.db import migrations, models


def normalize_specimen_environment(apps, schema_editor):
    Climate = apps.get_model("locations", "Climate")
    Habitat = apps.get_model("locations", "Habitat")
    SpecimenLocation = apps.get_model("specimens", "SpecimenLocation")

    climates = {item.name.casefold(): item for item in Climate.objects.all()}
    habitats = {item.name.casefold(): item for item in Habitat.objects.all()}
    for record in SpecimenLocation.objects.all().order_by("id"):
        climate_name = record.climate_text.strip()
        habitat_name = record.habitat_text.strip()
        if climate_name:
            key = climate_name.casefold()
            climate = climates.get(key)
            if climate is None:
                climate = Climate.objects.create(name=climate_name)
                climates[key] = climate
            record.climate_id = climate.pk
        if habitat_name:
            key = habitat_name.casefold()
            habitat = habitats.get(key)
            if habitat is None:
                habitat = Habitat.objects.create(name=habitat_name)
                habitats[key] = habitat
            record.habitat_id = habitat.pk
        record.save(update_fields=["climate", "habitat"])


class Migration(migrations.Migration):
    dependencies = [
        ("locations", "0003_normalize_climates_and_habitats"),
        ("specimens", "0004_specimen_is_published"),
    ]

    operations = [
        migrations.RenameField(
            model_name="specimenlocation",
            old_name="climate",
            new_name="climate_text",
        ),
        migrations.RenameField(
            model_name="specimenlocation",
            old_name="habitat",
            new_name="habitat_text",
        ),
        migrations.AddField(
            model_name="specimenlocation",
            name="climate",
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name="specimen_links", to="locations.climate"),
        ),
        migrations.AddField(
            model_name="specimenlocation",
            name="habitat",
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name="specimen_links", to="locations.habitat"),
        ),
        migrations.RunPython(normalize_specimen_environment, migrations.RunPython.noop),
        migrations.RemoveField(model_name="specimenlocation", name="climate_text"),
        migrations.RemoveField(model_name="specimenlocation", name="habitat_text"),
    ]
