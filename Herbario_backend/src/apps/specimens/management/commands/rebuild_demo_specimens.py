from __future__ import annotations

from django.core.management.base import BaseCommand
from django.db import transaction

from apps.collections_app.models import Collection
from apps.locations.models import ClimateHabitat, Location
from apps.media.models import HerbariumImage, HerbariumImageVariant
from apps.specimens.models import Specimen, SpecimenLocation
from apps.specimens.seeders.complete_specimen import (
    DEMO_COLLECTION_NAMES,
    DEMO_LOCATION_COMMENT_PREFIX,
    seed_complete_specimen,
)


class Command(BaseCommand):
    help = (
        "Elimina los especímenes, imágenes, ubicaciones y colecciones demo, "
        "y vuelve a crear los especímenes sin imágenes ni colecciones."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--database",
            default="default",
            help="Alias de la base de datos en la que se reconstruirán los datos.",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Muestra el alcance de la limpieza sin modificar datos ni archivos.",
        )

    def handle(self, *args, **options):
        using = options["database"]
        demo_specimens = Specimen.all_objects.using(using).filter(
            catalog_code__startswith="HESP-DEMO-"
        )
        demo_specimen_ids = list(demo_specimens.values_list("pk", flat=True))
        demo_images = HerbariumImage.all_objects.using(using).filter(
            specimen_id__in=demo_specimen_ids
        )
        demo_image_ids = list(demo_images.values_list("pk", flat=True))
        demo_variants = HerbariumImageVariant.objects.using(using).filter(
            image_id__in=demo_image_ids
        )
        demo_collections = Collection.all_objects.using(using).filter(
            name__in=DEMO_COLLECTION_NAMES
        )

        counts = {
            "specimens": len(demo_specimen_ids),
            "locations": SpecimenLocation.objects.using(using)
            .filter(specimen_id__in=demo_specimen_ids)
            .count(),
            "images": len(demo_image_ids),
            "variants": demo_variants.count(),
            "collections": demo_collections.count(),
        }
        self.stdout.write(
            "Alcance demo: "
            f"{counts['specimens']} especímenes, {counts['locations']} relaciones de ubicación, "
            f"{counts['images']} imágenes, {counts['variants']} variantes y "
            f"{counts['collections']} colecciones."
        )

        if options["dry_run"]:
            self.stdout.write(
                self.style.WARNING("Simulación completada; no se realizaron cambios.")
            )
            return

        stored_files = []
        for image in demo_images:
            if image.image and image.image.name:
                stored_files.append((image.image.storage, image.image.name))
        for variant in demo_variants:
            if variant.file and variant.file.name:
                stored_files.append((variant.file.storage, variant.file.name))

        with transaction.atomic(using=using):
            demo_variants.delete()
            demo_images.hard_delete()
            demo_collections.hard_delete()
            SpecimenLocation.objects.using(using).filter(
                specimen_id__in=demo_specimen_ids
            ).delete()
            demo_specimens.hard_delete()

            orphan_demo_locations = Location.all_objects.using(using).filter(
                comment__startswith=DEMO_LOCATION_COMMENT_PREFIX,
                specimen_links__isnull=True,
            )
            orphan_location_ids = list(
                orphan_demo_locations.values_list("pk", flat=True).distinct()
            )
            ClimateHabitat.all_objects.using(using).filter(
                location_id__in=orphan_location_ids
            ).hard_delete()
            Location.all_objects.using(using).filter(
                pk__in=orphan_location_ids
            ).hard_delete()

            seed_complete_specimen(using=using, verbosity=0)

        deleted_files = 0
        failed_files = []
        seen_files = set()
        for storage, name in stored_files:
            storage_key = (id(storage), name)
            if storage_key in seen_files:
                continue
            seen_files.add(storage_key)
            try:
                if storage.exists(name):
                    storage.delete(name)
                    deleted_files += 1
            except OSError as error:
                failed_files.append(f"{name}: {error}")

        self.stdout.write(
            self.style.SUCCESS(
                "Datos demo reconstruidos: 30 especímenes, 60 ubicaciones únicas, "
                "sin imágenes y sin colecciones demo. "
                f"Archivos eliminados: {deleted_files}."
            )
        )
        for failure in failed_files:
            self.stderr.write(self.style.WARNING(f"No se pudo eliminar {failure}"))
