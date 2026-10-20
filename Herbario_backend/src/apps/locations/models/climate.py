from django.db import models
from django.db.models.functions import Lower

from apps.common.models import SoftDeleteModel


class Climate(SoftDeleteModel):
    name = models.CharField(max_length=100)

    class Meta:
        db_table = "locations_climate"
        ordering = ["name"]
        constraints = [
            models.UniqueConstraint(Lower("name"), name="unique_climate_name_ci")
        ]

    def __str__(self) -> str:
        return self.name
