import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("locations", "0001_initial")]

    operations = [
        migrations.AlterField(
            model_name="location",
            name="latitude",
            field=models.DecimalField(
                decimal_places=8,
                max_digits=10,
                validators=[
                    django.core.validators.MinValueValidator(-90),
                    django.core.validators.MaxValueValidator(90),
                ],
            ),
        ),
        migrations.AlterField(
            model_name="location",
            name="longitude",
            field=models.DecimalField(
                decimal_places=8,
                max_digits=11,
                validators=[
                    django.core.validators.MinValueValidator(-180),
                    django.core.validators.MaxValueValidator(180),
                ],
            ),
        ),
    ]
