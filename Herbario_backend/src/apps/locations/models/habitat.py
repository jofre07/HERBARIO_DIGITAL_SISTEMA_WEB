from django.db import models
from django.db.models.functions import Lower

from apps.common.models import SoftDeleteModel


class Habitat(SoftDeleteModel):
    name = models.CharField(max_length=100)

    class Meta:
        db_table = "locations_habitat"
        ordering = ["name"]
        constraints = [
            models.UniqueConstraint(Lower("name"), name="unique_habitat_name_ci")
        ]

    def __str__(self) -> str:
        return self.name
