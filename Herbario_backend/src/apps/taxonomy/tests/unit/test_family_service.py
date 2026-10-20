import pytest

from apps.taxonomy.models import Family
from apps.taxonomy.services import FamilyService


@pytest.mark.django_db
def test_soft_delete_hides_family_from_default_manager():
    family = Family.objects.create(name="Asteraceae")
    FamilyService().soft_delete(family)
    assert Family.objects.filter(pk=family.pk).exists() is False
    assert Family.all_objects.filter(pk=family.pk, deleted=True).exists() is True
