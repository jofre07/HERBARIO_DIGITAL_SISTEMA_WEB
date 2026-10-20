from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("specimens", "0002_multiple_locations")]

    operations = [
        migrations.AddField(
            model_name="specimenlocation",
            name="marker_icon",
            field=models.CharField(
                choices=[
                    ("plant", "Planta"),
                    ("flower", "Flor"),
                    ("tree", "Árbol"),
                    ("leaf", "Hoja"),
                    ("herb", "Hierba"),
                ],
                default="plant",
                max_length=20,
            ),
        ),
    ]
