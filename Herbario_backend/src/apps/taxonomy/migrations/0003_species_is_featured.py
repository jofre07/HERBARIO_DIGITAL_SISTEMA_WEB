from django.db import migrations, models


def feature_initial_species(apps, schema_editor):
    Species = apps.get_model("taxonomy", "Species")
    Specimen = apps.get_model("specimens", "Specimen")

    published_species_ids = Specimen.objects.filter(
        deleted=False,
        is_published=True,
    ).values_list("species_id", flat=True)
    featured_ids = list(
        Species.objects.filter(
            deleted=False,
            id__in=published_species_ids,
        )
        .order_by("name")
        .values_list("id", flat=True)[:4]
    )
    Species.objects.filter(id__in=featured_ids).update(is_featured=True)


def clear_featured_species(apps, schema_editor):
    Species = apps.get_model("taxonomy", "Species")
    Species.objects.update(is_featured=False)


class Migration(migrations.Migration):
    dependencies = [
        ("specimens", "0004_specimen_is_published"),
        ("taxonomy", "0002_default_common_name_region"),
    ]

    operations = [
        migrations.AddField(
            model_name="species",
            name="is_featured",
            field=models.BooleanField(db_index=True, default=False),
        ),
        migrations.RunPython(feature_initial_species, clear_featured_species),
    ]
