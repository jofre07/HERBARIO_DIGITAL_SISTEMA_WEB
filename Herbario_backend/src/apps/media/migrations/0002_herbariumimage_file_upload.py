from django.db import migrations, models

import apps.media.models.herbarium_image


class Migration(migrations.Migration):
    dependencies = [("media", "0001_initial")]

    operations = [
        migrations.AddField(
            model_name="herbariumimage",
            name="image",
            field=models.ImageField(
                blank=True,
                null=True,
                upload_to=apps.media.models.herbarium_image.herbarium_image_upload_path,
            ),
        ),
        migrations.AlterField(
            model_name="herbariumimage",
            name="url",
            field=models.URLField(blank=True),
        ),
    ]
