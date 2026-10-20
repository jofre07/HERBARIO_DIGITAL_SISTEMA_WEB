import pytest

from apps.common.exceptions import ConflictError
from apps.taxonomy.models import Family, Genus, Species
from apps.taxonomy.services import SpeciesService


@pytest.mark.django_db
def test_species_service_limits_featured_species_to_four():
    family = Family.objects.create(name="Featured service family")
    genus = Genus.objects.create(name="Featured service genus", family=family)
    service = SpeciesService()

    for index in range(4):
        service.create(
            data={
                "name": f"Featured service species {index}",
                "genus": genus,
                "is_featured": True,
            }
        )

    regular = Species.objects.create(name="Regular service species", genus=genus)

    with pytest.raises(ConflictError):
        service.update(regular, data={"is_featured": True})


@pytest.mark.django_db
def test_species_service_can_replace_a_featured_species():
    family = Family.objects.create(name="Replacement family")
    genus = Genus.objects.create(name="Replacement genus", family=family)
    service = SpeciesService()
    current = service.create(
        data={"name": "Current featured", "genus": genus, "is_featured": True}
    )
    replacement = Species.objects.create(name="Replacement featured", genus=genus)

    service.update(current, data={"is_featured": False})
    service.update(replacement, data={"is_featured": True})

    assert Species.objects.get(pk=current.pk).is_featured is False
    assert Species.objects.get(pk=replacement.pk).is_featured is True
