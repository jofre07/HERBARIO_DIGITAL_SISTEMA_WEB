from django.db import migrations, models


def publish_existing_specimens(apps, schema_editor):
    Specimen = apps.get_model("specimens", "Specimen")
    Specimen.objects.update(is_published=True)


def unpublish_existing_specimens(apps, schema_editor):
    Specimen = apps.get_model("specimens", "Specimen")
    Specimen.objects.update(is_published=False)


class Migration(migrations.Migration):
    dependencies = [("specimens", "0003_specimenlocation_marker_icon")]

    operations = [
        migrations.AddField(
            model_name="specimen",
            name="is_published",
            field=models.BooleanField(db_index=True, default=False),
        ),
        migrations.RunPython(publish_existing_specimens, unpublish_existing_specimens),
    ]
