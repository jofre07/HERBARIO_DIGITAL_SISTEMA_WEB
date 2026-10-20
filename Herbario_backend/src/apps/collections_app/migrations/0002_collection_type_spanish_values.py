from django.db import migrations, models


FORWARD_VALUES = {
    "featured": "destacada",
    "threatened": "amenazada",
    "recent": "reciente",
}

REVERSE_VALUES = {value: key for key, value in FORWARD_VALUES.items()}


def translate_collection_types(apps, schema_editor):
    collection = apps.get_model("collections_app", "Collection")
    for old_value, new_value in FORWARD_VALUES.items():
        collection.objects.filter(collection_type=old_value).update(
            collection_type=new_value
        )


def restore_collection_types(apps, schema_editor):
    collection = apps.get_model("collections_app", "Collection")
    for current_value, old_value in REVERSE_VALUES.items():
        collection.objects.filter(collection_type=current_value).update(
            collection_type=old_value
        )


class Migration(migrations.Migration):
    dependencies = [
        ("collections_app", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(
            translate_collection_types,
            restore_collection_types,
        ),
        migrations.AlterField(
            model_name="collection",
            name="collection_type",
            field=models.CharField(
                choices=[
                    ("destacada", "Especies destacadas"),
                    ("amenazada", "Especies amenazadas"),
                    ("reciente", "Nuevos registros"),
                    ("local", "Interés local"),
                    ("general", "General"),
                ],
                default="general",
                max_length=20,
            ),
        ),
    ]
