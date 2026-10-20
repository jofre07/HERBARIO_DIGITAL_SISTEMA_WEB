import pytest
from rest_framework.test import APIClient

from apps.collections_app.models import Collection
from apps.locations.models import Location
from apps.media.models import HerbariumImage
from apps.specimens.models import Specimen, SpecimenLocation
from apps.taxonomy.models import Family, Genus, Species


@pytest.mark.django_db
def test_drafts_do_not_leak_into_public_modules():
    family = Family.objects.create(name="Publication family")
    genus = Genus.objects.create(name="Publication genus", family=family)
    published_species = Species.objects.create(name="Published species", genus=genus)
    draft_species = Species.objects.create(name="Draft-only species", genus=genus)
    published = Specimen.objects.create(
        catalog_code="PUB-001",
        species=published_species,
        is_published=True,
    )
    draft = Specimen.objects.create(
        catalog_code="DRAFT-001",
        species=draft_species,
        is_published=False,
    )
    published_location = Location.objects.create(
        name="Published location", latitude="-0.10000000", longitude="-80.10000000"
    )
    draft_location = Location.objects.create(
        name="Draft location", latitude="-0.20000000", longitude="-80.20000000"
    )
    SpecimenLocation.objects.create(
        specimen=published,
        location=published_location,
        habitat="Published habitat",
        is_primary=True,
    )
    SpecimenLocation.objects.create(
        specimen=draft,
        location=draft_location,
        habitat="Draft habitat",
        is_primary=True,
    )
    HerbariumImage.objects.create(
        specimen=published, url="https://example.com/published.jpg"
    )
    HerbariumImage.objects.create(
        specimen=draft, url="https://example.com/draft.jpg"
    )
    collection = Collection.objects.create(name="Publication collection")
    collection.specimens.add(published, draft)
    client = APIClient()

    specimens = client.get("/api/public/specimens/").data
    map_points = client.get("/api/public/map/points/").data
    media = client.get("/api/public/media/").data
    catalog = client.get("/api/public/catalog/species/").data
    collections = client.get("/api/public/collections/").data
    options = client.get("/api/public/filter-options/").data
    stats = client.get("/api/public/stats/").data

    assert [item["catalog_code"] for item in specimens["results"]] == ["PUB-001"]
    assert [item["catalog_code"] for item in map_points] == ["PUB-001"]
    assert [item["url"] for item in media["results"]] == [
        "https://example.com/published.jpg"
    ]
    assert [item["name"] for item in catalog["results"]] == ["Published species"]
    assert collections["results"][0]["specimen_count"] == 1
    assert "Published location" in options["locations"]
    assert "Draft location" not in options["locations"]
    assert "Published habitat" in options["habitats"]
    assert "Draft habitat" not in options["habitats"]
    assert stats["specimens"] == 1
    assert stats["images"] == 1
