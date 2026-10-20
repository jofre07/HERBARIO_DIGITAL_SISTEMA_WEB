from django.db import migrations, models
from django.db.models.functions import Lower


class Migration(migrations.Migration):
    dependencies = [("locations", "0003_normalize_climates_and_habitats")]

    operations = [
        migrations.AlterField(
            model_name="climate",
            name="name",
            field=models.CharField(max_length=100),
        ),
        migrations.AlterField(
            model_name="habitat",
            name="name",
            field=models.CharField(max_length=100),
        ),
        migrations.AddConstraint(
            model_name="climate",
            constraint=models.UniqueConstraint(
                Lower("name"), name="unique_climate_name_ci"
            ),
        ),
        migrations.AddConstraint(
            model_name="habitat",
            constraint=models.UniqueConstraint(
                Lower("name"), name="unique_habitat_name_ci"
            ),
        ),
    ]
