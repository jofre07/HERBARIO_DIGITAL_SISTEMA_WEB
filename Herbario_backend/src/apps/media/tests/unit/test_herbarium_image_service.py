import pytest

from apps.common.exceptions import ValidationError
from apps.media.models import HerbariumImage
from apps.media.services import HerbariumImageService
from apps.specimens.models import Specimen
from apps.taxonomy.models import Family, Genus, Species


@pytest.mark.django_db
def test_soft_delete_hides_image_from_default_manager():
    family = Family.objects.create(name="Poaceae")
    genus = Genus.objects.create(name="Zea", family=family)
    species = Species.objects.create(name="mays", genus=genus)
    specimen = Specimen.objects.create(catalog_code="SP-IMG", species=species)
    image = HerbariumImage.objects.create(
        specimen=specimen,
        url="https://example.com/photo.jpg",
    )

    HerbariumImageService().soft_delete(image)

    assert HerbariumImage.objects.filter(pk=image.pk).exists() is False
    assert HerbariumImage.all_objects.filter(pk=image.pk, deleted=True).exists() is True


@pytest.mark.django_db
def test_specimen_cannot_have_more_than_five_images():
    family = Family.objects.create(name="Fabaceae")
    genus = Genus.objects.create(name="Inga", family=family)
    species = Species.objects.create(name="edulis", genus=genus)
    specimen = Specimen.objects.create(catalog_code="SP-LIMIT", species=species)
    for index in range(5):
        HerbariumImage.objects.create(
            specimen=specimen,
            url=f"https://example.com/photo-{index}.jpg",
        )

    with pytest.raises(ValidationError, match="máximo de 5"):
        HerbariumImageService().create(
            data={"specimen": specimen, "url": "https://example.com/photo-6.jpg"}
        )
