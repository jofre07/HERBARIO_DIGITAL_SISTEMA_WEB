from rest_framework.test import APIClient

from apps.collections_app.models import Collection
from apps.specimens.models import Specimen
from apps.taxonomy.models import Family, Genus, Species


def test_collections_list_endpoint_returns_200(db):
    collection = Collection.objects.create(
        name="Andean Flora", collection_type=Collection.CollectionType.AMENAZADA
    )
    family = Family.objects.create(name="Andean family")
    genus = Genus.objects.create(name="Andean genus", family=family)
    species = Species.objects.create(name="Andean species", genus=genus)
    specimen = Specimen.objects.create(
        catalog_code="AND-001", species=species, is_published=True
    )
    collection.specimens.add(specimen)
    response = APIClient().get("/api/public/collections/")
    assert response.status_code == 200
    item = response.data["results"][0]
    assert item["collection_type_label"] == "Especies amenazadas"
    assert item["specimen_count"] == 1
    assert item["species_count"] == 1
    assert item["location_count"] == 0
    assert item["image_url"] is None
    assert item["family_names"] == ["Andean family"]
    assert item["location_names"] == []
    assert item["conservation_statuses"] == []

    filtered = APIClient().get(
        "/api/public/collections/", {"collection_type": Collection.CollectionType.AMENAZADA}
    )
    assert filtered.status_code == 200
    assert filtered.data["count"] == 1
