import pytest

from apps.taxonomy.models import Language
from apps.taxonomy.seeders import seed_languages


@pytest.mark.django_db
def test_seed_languages_creates_and_restores_catalog():
    seed_languages(using="default", verbosity=0)
    spanish = Language.objects.get(code="es")
    spanish.soft_delete()

    seed_languages(using="default", verbosity=0)

    spanish.refresh_from_db()
    assert spanish.name == "Español"
    assert spanish.deleted is False
    assert set(Language.objects.values_list("code", flat=True)) >= {"es", "en", "qu", "jiv"}
