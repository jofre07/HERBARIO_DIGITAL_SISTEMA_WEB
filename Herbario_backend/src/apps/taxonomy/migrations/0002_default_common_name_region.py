from django.db import migrations, models


def set_coast_region(apps, schema_editor):
    common_name = apps.get_model("taxonomy", "CommonName")
    common_name._base_manager.using(schema_editor.connection.alias).update(region="Costa")


class Migration(migrations.Migration):
    dependencies = [("taxonomy", "0001_initial")]

    operations = [
        migrations.RunPython(set_coast_region, migrations.RunPython.noop),
        migrations.AlterField(
            model_name="commonname",
            name="region",
            field=models.CharField(default="Costa", editable=False, max_length=120),
        ),
    ]
