import apps.media.models.herbarium_image
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [("media", "0002_herbariumimage_file_upload")]

    operations = [
        migrations.CreateModel(
            name="HerbariumImageVariant",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("variant", models.CharField(choices=[("thumbnail", "Miniatura"), ("medium", "Mediana"), ("large", "Grande")], max_length=16)),
                ("file", models.ImageField(upload_to=apps.media.models.herbarium_image.herbarium_variant_upload_path)),
                ("width", models.PositiveIntegerField()),
                ("height", models.PositiveIntegerField()),
                ("file_size", models.PositiveIntegerField()),
                ("format", models.CharField(default="webp", max_length=10)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("image", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="variants", to="media.herbariumimage")),
            ],
            options={
                "db_table": "media_herbariumimagevariant",
                "constraints": [models.UniqueConstraint(fields=("image", "variant"), name="unique_herbarium_image_variant")],
            },
        ),
    ]
