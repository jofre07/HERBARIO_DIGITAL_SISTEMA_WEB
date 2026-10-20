from io import BytesIO

import pytest
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from PIL import Image
from rest_framework.test import APIClient

from apps.common.api.ids import encode_external_id, model_namespace
from apps.media.models import HerbariumImage, HerbariumImageVariant
from apps.specimens.models import Specimen
from apps.taxonomy.models import Family, Genus, Species


def uploaded_image(name: str = "specimen.png") -> SimpleUploadedFile:
    content = BytesIO()
    Image.new("RGB", (20, 20), "green").save(content, format="PNG")
    return SimpleUploadedFile(name, content.getvalue(), content_type="image/png")


@pytest.mark.django_db
def test_list_media_returns_ok():
    family = Family.objects.create(name="Rubiaceae")
    genus = Genus.objects.create(name="Coffea", family=family)
    species = Species.objects.create(name="arabica", genus=genus)
    specimen = Specimen.objects.create(catalog_code="SP-MED", species=species, is_published=True)
    first_image = HerbariumImage.objects.create(
        specimen=specimen,
        url="https://example.com/coffee.jpg",
        credit="Herbario",
    )
    second_image = HerbariumImage.objects.create(
        specimen=specimen,
        url="https://example.com/coffee-2.jpg",
    )

    client = APIClient()
    user = get_user_model().objects.create_user(username="media", password="secret123")
    client.force_authenticate(user=user)
    response = client.get("/api/media/")
    assert response.status_code == 200
    item = response.data["results"][0]
    assert response.data["count"] == 1
    assert item == {
        "specimen_id": encode_external_id(specimen.pk, namespace=model_namespace(Specimen)),
        "catalog_code": "SP-MED",
        "image_count": 2,
        "cover": {
            "id": encode_external_id(
                second_image.pk, namespace=model_namespace(HerbariumImage)
            ),
            "thumbnail_url": "https://example.com/coffee-2.jpg",
            "credit": "",
        },
    }

    filtered = client.get(
        "/api/media/",
        {"family_name": "rubia", "species_name": "arab", "ordering": "species"},
    )
    assert filtered.status_code == 200
    assert filtered.data["count"] == 1

    specimen_external_id = encode_external_id(
        specimen.pk,
        namespace=model_namespace(Specimen),
    )
    detail = client.get(f"/api/media/specimens/{specimen_external_id}/")
    assert detail.status_code == 200
    assert detail.data == {
        "specimen_id": encode_external_id(specimen.pk, namespace=model_namespace(Specimen)),
        "catalog_code": "SP-MED",
        "images": [
            {
                "id": encode_external_id(
                    second_image.pk, namespace=model_namespace(HerbariumImage)
                ),
                "credit": "",
                "variants": {
                    "thumbnail": {"url": "https://example.com/coffee-2.jpg"},
                    "large": {"url": "https://example.com/coffee-2.jpg"},
                },
            },
            {
                "id": encode_external_id(
                    first_image.pk, namespace=model_namespace(HerbariumImage)
                ),
                "credit": "Herbario",
                "variants": {
                    "thumbnail": {"url": "https://example.com/coffee.jpg"},
                    "large": {"url": "https://example.com/coffee.jpg"},
                },
            },
        ],
    }


@pytest.mark.django_db
def test_upload_image_stores_file_and_returns_media_url(tmp_path, settings):
    settings.MEDIA_ROOT = tmp_path
    family = Family.objects.create(name="Asteraceae")
    genus = Genus.objects.create(name="Helianthus", family=family)
    species = Species.objects.create(name="annuus", genus=genus)
    specimen = Specimen.objects.create(catalog_code="SP-UPLOAD", species=species)
    user = get_user_model().objects.create_superuser(
        username="media-admin", email="media@example.com", password="secret123"
    )
    client = APIClient()
    client.force_authenticate(user=user)

    options_response = client.get("/api/media/specimen-options/")
    assert options_response.status_code == 200
    assert options_response.data == [
        {
            "id": encode_external_id(specimen.pk, namespace=model_namespace(Specimen)),
            "catalog_code": "SP-UPLOAD",
        }
    ]

    response = client.post(
        "/api/media/",
        {
            "specimen_id": encode_external_id(specimen.pk, namespace=model_namespace(Specimen)),
            "image": uploaded_image(),
            "credit": "Herbario",
        },
        format="multipart",
    )

    assert response.status_code == 201
    stored = HerbariumImage.objects.get(specimen=specimen)
    assert stored.image.name.startswith(f"specimens/{specimen.pk}/images/")
    assert stored.image.storage.exists(stored.image.name)
    variants = list(stored.variants.order_by("variant"))
    assert {variant.variant for variant in variants} == {
        HerbariumImageVariant.THUMBNAIL,
        HerbariumImageVariant.MEDIUM,
        HerbariumImageVariant.LARGE,
    }
    assert all(variant.format == "webp" for variant in variants)
    assert all(variant.width == 20 and variant.height == 20 for variant in variants)
    assert all(variant.file.storage.exists(variant.file.name) for variant in variants)
    assert response.data["url"] == response.data["variants"]["medium"]["url"]
    assert response.data["original_url"].endswith(stored.image.url)
