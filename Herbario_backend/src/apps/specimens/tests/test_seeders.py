import pytest
from django.contrib.auth import get_user_model
from django.core.management import call_command

from apps.collections_app.models import Collection
from apps.collectors.models import Collector
from apps.locations.models import ClimateHabitat, Location
from apps.media.models import HerbariumImage
from apps.roles.models import Role
from apps.specimens.models import Specimen, SpecimenLocation
from apps.specimens.seeders.complete_specimen import (
    COLLECTOR_NAMES,
    DEMO_COLLECTION_NAMES,
    DEMO_SPECIMEN_COUNT,
    TAXA,
    _is_within_manabi,
)
from apps.taxonomy.models import (
    CommonName,
    ConservationStatus,
    Family,
    Genus,
    Species,
    Translation,
)
from apps.users.models import AuditLog


@pytest.mark.django_db
def test_complete_specimen_seeder_is_idempotent_and_skips_excluded_modules():
    user_count = get_user_model().objects.count()
    role_count = Role.objects.count()
    audit_count = AuditLog.objects.count()
    call_command("seed_complete_specimen", verbosity=0)
    call_command("seed_complete_specimen", verbosity=0)

    demo_specimens = Specimen.objects.filter(catalog_code__startswith="HESP-DEMO-")
    assert Family.objects.filter(name__in=[item[0] for item in TAXA]).count() == 10
    assert Genus.objects.filter(name__in=[item[1] for item in TAXA]).count() == 10
    assert Species.objects.filter(name__in=[item[2] for item in TAXA]).count() == 10
    assert CommonName.objects.filter(species__in=specimen_species(demo_specimens)).count() == 10
    assert (
        Translation.objects.filter(
            common_name__species__in=specimen_species(demo_specimens)
        ).count()
        == 10
    )
    assert (
        ConservationStatus.objects.filter(species__in=specimen_species(demo_specimens)).count()
        == 10
    )
    assert Collector.objects.filter(name__in=COLLECTOR_NAMES).count() == 10
    assert demo_specimens.count() == DEMO_SPECIMEN_COUNT
    assert demo_specimens.filter(is_published=True).count() == DEMO_SPECIMEN_COUNT - 2
    assert demo_specimens.filter(is_published=False).count() == 2
    assert SpecimenLocation.objects.filter(specimen__in=demo_specimens).count() == 60
    demo_locations = Location.objects.filter(specimen_links__specimen__in=demo_specimens).distinct()
    assert demo_locations.count() == 60
    assert ClimateHabitat.objects.filter(location__in=demo_locations).count() == 60
    assert len(set(demo_locations.values_list("latitude", "longitude"))) == 60
    assert all(
        _is_within_manabi(latitude, longitude)
        for latitude, longitude in demo_locations.values_list("latitude", "longitude")
    )
    assert (
        SpecimenLocation.objects.filter(specimen__in=demo_specimens, is_primary=True).count()
        == DEMO_SPECIMEN_COUNT
    )
    assert Collection.objects.filter(name__in=DEMO_COLLECTION_NAMES).count() == 0
    assert Collection.objects.filter(specimens__in=demo_specimens).count() == 0
    assert HerbariumImage.objects.filter(specimen__in=demo_specimens).count() == 0
    assert get_user_model().objects.count() == user_count
    assert Role.objects.count() == role_count
    assert AuditLog.objects.count() == audit_count


@pytest.mark.django_db(transaction=True)
def test_rebuild_demo_specimens_removes_images_and_collections_before_reseeding():
    call_command("seed_complete_specimen", verbosity=0)
    specimen = Specimen.objects.get(catalog_code="HESP-DEMO-001")
    HerbariumImage.objects.create(
        specimen=specimen,
        url="https://example.com/demo.jpg",
        credit="Demo",
    )
    Collection.objects.create(
        name=DEMO_COLLECTION_NAMES[0],
        description="Colección temporal",
    ).specimens.add(specimen)

    call_command("rebuild_demo_specimens", verbosity=0)

    demo_specimens = Specimen.objects.filter(catalog_code__startswith="HESP-DEMO-")
    demo_locations = Location.objects.filter(specimen_links__specimen__in=demo_specimens).distinct()
    assert demo_specimens.count() == DEMO_SPECIMEN_COUNT
    assert SpecimenLocation.objects.filter(specimen__in=demo_specimens).count() == 60
    assert demo_locations.count() == 60
    assert len(set(demo_locations.values_list("latitude", "longitude"))) == 60
    assert HerbariumImage.all_objects.filter(specimen__in=demo_specimens).count() == 0
    assert Collection.all_objects.filter(name__in=DEMO_COLLECTION_NAMES).count() == 0


def specimen_species(specimens):
    return Species.objects.filter(specimens__in=specimens).distinct()
