from __future__ import annotations

from django.core.management.base import BaseCommand, CommandError

from apps.media.models import HerbariumImage
from apps.media.services.image_variant_service import ImageVariantService


class Command(BaseCommand):
    help = "Genera las versiones WebP optimizadas de las imágenes originales existentes."

    def add_arguments(self, parser) -> None:
        parser.add_argument(
            "--force",
            action="store_true",
            help="Regenera las variantes aunque ya existan las tres versiones.",
        )
        parser.add_argument(
            "--image-id",
            type=int,
            help="Procesa únicamente el identificador interno indicado.",
        )

    def handle(self, *args, **options) -> None:
        queryset = HerbariumImage.objects.filter(image__isnull=False).exclude(image="")
        if options["image_id"]:
            queryset = queryset.filter(pk=options["image_id"])
            if not queryset.exists():
                raise CommandError("No se encontró una imagen local con ese identificador.")

        service = ImageVariantService()
        expected_count = len(service.SPECS)
        processed = skipped = failed = 0

        for image in queryset.prefetch_related("variants").iterator(chunk_size=100):
            if not options["force"] and len(image.variants.all()) == expected_count:
                skipped += 1
                continue
            try:
                service.generate(image)
                processed += 1
            except Exception as exc:
                failed += 1
                self.stderr.write(self.style.ERROR(f"Imagen {image.pk}: {exc}"))

        self.stdout.write(
            self.style.SUCCESS(
                f"Variantes generadas: {processed}; omitidas: {skipped}; errores: {failed}."
            )
        )
