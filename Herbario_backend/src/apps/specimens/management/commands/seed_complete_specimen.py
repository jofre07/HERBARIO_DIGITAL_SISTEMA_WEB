from django.core.management.base import BaseCommand

from apps.specimens.seeders import seed_complete_specimen


class Command(BaseCommand):
    help = "Crea un espécimen demostrativo completo sin registros de imágenes."

    def add_arguments(self, parser):
        parser.add_argument(
            "--database",
            default="default",
            help="Alias de la base de datos en la que se crearán los datos.",
        )

    def handle(self, *args, **options):
        seed_complete_specimen(
            using=options["database"],
            verbosity=options["verbosity"],
        )
