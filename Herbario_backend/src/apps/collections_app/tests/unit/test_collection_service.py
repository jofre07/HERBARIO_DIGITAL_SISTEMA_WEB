import pytest

from apps.collections_app.models import Collection
from apps.collections_app.services import CollectionService


@pytest.mark.django_db
def test_soft_delete_hides_collection_from_default_manager():
    collection = Collection.objects.create(name="Andean Flora")

    CollectionService().soft_delete(collection)

    assert Collection.objects.filter(pk=collection.pk).exists() is False
    assert Collection.all_objects.filter(pk=collection.pk, deleted=True).exists() is True
