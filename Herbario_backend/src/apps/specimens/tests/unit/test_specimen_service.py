import pytest

from apps.specimens.models import Specimen
from apps.specimens.services import SpecimenService
from apps.taxonomy.models import Family, Genus, Species


@pytest.mark.django_db
def test_soft_delete_hides_specimen_from_default_manager():
    family = Family.objects.create(name="Plantaginaceae")
    genus = Genus.objects.create(name="Plantago", family=family)
    species = Species.objects.create(name="major", genus=genus)
    specimen = Specimen.objects.create(catalog_code="SP-DEL", species=species)

    SpecimenService().soft_delete(specimen)

    assert Specimen.objects.filter(pk=specimen.pk).exists() is False
    assert Specimen.all_objects.filter(pk=specimen.pk, deleted=True).exists() is True
