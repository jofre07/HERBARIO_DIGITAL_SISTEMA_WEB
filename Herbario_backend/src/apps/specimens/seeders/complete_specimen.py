from __future__ import annotations

import json
from datetime import date, timedelta
from decimal import Decimal
from functools import lru_cache
from pathlib import Path
from typing import Any

from django.db import transaction

from apps.collectors.models import Collector
from apps.locations.models import Climate, ClimateHabitat, Habitat, Location
from apps.specimens.models import Specimen, SpecimenLocation
from apps.taxonomy.models import (
    CommonName,
    ConservationStatus,
    Family,
    Genus,
    Language,
    Species,
    Status,
    Translation,
)

DEMO_CATALOG_CODE = "HESP-DEMO-001"
DEMO_SPECIMEN_COUNT = 30
DEMO_LOCATION_COMMENT_PREFIX = "Punto de recolección demostrativo:"
DEMO_COLLECTION_NAMES = (
    "Especímenes demostrativos",
    "Especies amenazadas demo",
    "Nuevos registros demo",
    "Flora de interés local",
    "Colección general demo",
)

TAXA = [
    ("Fabaceae", "Erythrina", "poeppigiana", "Porotón", "Coral tree", "LC"),
    ("Orchidaceae", "Epidendrum", "radicans", "Epidendro", "Crucifix orchid", "NE"),
    ("Asteraceae", "Helianthus", "annuus", "Girasol", "Sunflower", "LC"),
    ("Rubiaceae", "Coffea", "arabica", "Café", "Coffee", "VU"),
    ("Myrtaceae", "Psidium", "guajava", "Guayaba", "Guava", "LC"),
    ("Lauraceae", "Persea", "americana", "Aguacate", "Avocado", "LC"),
    ("Melastomataceae", "Miconia", "calvescens", "Miconia", "Velvet tree", "NE"),
    ("Malvaceae", "Ceiba", "pentandra", "Ceibo", "Kapok tree", "LC"),
    ("Araceae", "Anthurium", "andraeanum", "Anturio", "Flamingo flower", "NE"),
    ("Bromeliaceae", "Tillandsia", "usneoides", "Barba de viejo", "Spanish moss", "LC"),
]

COLLECTOR_NAMES = [
    "María Zambrano",
    "José Mendoza",
    "Ana Cedeño",
    "Carlos Alcívar",
    "Luisa Moreira",
    "Pedro Vera",
    "Sofía Loor",
    "Miguel Macías",
    "Elena Andrade",
    "Diego Santana",
]

LOCATION_DATA = [
    (
        "Bosque Protector Cerro Pata de Pájaro",
        "-0.59321458",
        "-80.14273691",
        "Tropical húmedo",
        "Bosque húmedo premontano",
    ),
    (
        "Estación Experimental Calceta",
        "-0.84214567",
        "-80.16397842",
        "Tropical subhúmedo",
        "Sistema agroforestal",
    ),
    (
        "Reserva Ecológica Mache Chindul",
        "0.15000000",
        "-79.95000000",
        "Tropical lluvioso",
        "Bosque siempreverde",
    ),
    (
        "Bosque Seco de Montecristi",
        "-1.04728651",
        "-80.65714382",
        "Tropical seco",
        "Bosque seco tropical",
    ),
    (
        "Humedal La Segua",
        "-0.69915246",
        "-80.19586431",
        "Tropical subhúmedo",
        "Humedal de agua dulce",
    ),
    (
        "Refugio de Vida Silvestre Pacoche",
        "-1.05634827",
        "-80.87125469",
        "Tropical húmedo",
        "Bosque de garúa",
    ),
    (
        "Jardín Botánico de Portoviejo",
        "-1.04472163",
        "-80.46287351",
        "Tropical seco",
        "Jardín botánico",
    ),
    (
        "Valle del Río Carrizal",
        "-0.88143627",
        "-80.20571384",
        "Tropical subhúmedo",
        "Bosque ribereño",
    ),
    ("Cerro Jaboncillo", "-1.07251843", "-80.57934126", "Tropical seco", "Matorral seco"),
    ("Manglar La Boca", "-0.79943621", "-80.50874392", "Tropical costero", "Manglar estuarino"),
]

STATUS_NAMES = {
    "LC": "Preocupación menor",
    "VU": "Vulnerable",
    "NE": "No evaluado",
}


@lru_cache(maxsize=1)
def _manabi_boundary_rings() -> tuple[tuple[tuple[float, float], ...], ...]:
    boundary_path = Path(__file__).with_name("data") / "manabi.geojson"
    geojson = json.loads(boundary_path.read_text(encoding="utf-8"))
    coordinates = geojson["features"][0]["geometry"]["coordinates"]
    return tuple(tuple((float(x), float(y)) for x, y in ring) for ring in coordinates)


def _point_in_ring(longitude: float, latitude: float, ring) -> bool:
    inside = False
    for index, (x2, y2) in enumerate(ring):
        x1, y1 = ring[index - 1]
        if (y1 > latitude) != (y2 > latitude):
            intersection = (x2 - x1) * (latitude - y1) / (y2 - y1) + x1
            if longitude < intersection:
                inside = not inside
    return inside


def _is_within_manabi(latitude: Decimal, longitude: Decimal) -> bool:
    outer_ring, *holes = _manabi_boundary_rings()
    point = (float(longitude), float(latitude))
    return _point_in_ring(*point, outer_ring) and not any(
        _point_in_ring(*point, hole) for hole in holes
    )


def _demo_location_data(specimen_index: int, order: int) -> tuple[str, Decimal, Decimal, str, str]:
    """Return a stable, specimen-specific collection point near a demo site."""
    base_index = (
        (specimen_index - 1) % len(LOCATION_DATA)
        if order == 1
        else (specimen_index + 2) % len(LOCATION_DATA)
    )
    name, latitude, longitude, climate, habitat = LOCATION_DATA[base_index]
    point_number = (specimen_index - 1) * 2 + order
    latitude_offset = (Decimal(point_number) - Decimal("30.5")) * Decimal("0.00007000")
    longitude_offset = Decimal((point_number * 17) % 61 - 30) * Decimal("0.00007000")
    precision = Decimal("0.00000001")
    point_latitude = (Decimal(latitude) + latitude_offset).quantize(precision)
    point_longitude = (Decimal(longitude) + longitude_offset).quantize(precision)
    if not _is_within_manabi(point_latitude, point_longitude):
        raise ValueError(
            f"La ubicación demo {name} ({point_latitude}, {point_longitude}) "
            "está fuera de la provincia de Manabí."
        )
    return (
        name,
        point_latitude,
        point_longitude,
        climate,
        habitat,
    )


def _active_upsert(
    model,
    *,
    using: str,
    lookup: dict[str, Any],
    defaults: dict[str, Any],
):
    return model.all_objects.db_manager(using).update_or_create(
        **lookup,
        defaults={**defaults, "deleted": False, "deleted_at": None},
    )[0]


@transaction.atomic
def seed_complete_specimen(*, using: str = "default", verbosity: int = 1) -> Specimen:
    spanish = _active_upsert(
        Language,
        using=using,
        lookup={"code": "es"},
        defaults={"name": "Español", "native_name": "Español"},
    )
    english = _active_upsert(
        Language,
        using=using,
        lookup={"code": "en"},
        defaults={"name": "Inglés", "native_name": "English"},
    )

    species_records = []
    for family_name, genus_name, species_name, common, translated, status_code in TAXA:
        family = _active_upsert(
            Family,
            using=using,
            lookup={"name": family_name},
            defaults={"comment": f"Familia botánica {family_name} del catálogo demostrativo."},
        )
        genus = _active_upsert(
            Genus,
            using=using,
            lookup={"name": genus_name, "family": family},
            defaults={"comment": f"Género {genus_name} registrado para demostración."},
        )
        species = _active_upsert(
            Species,
            using=using,
            lookup={"name": species_name, "genus": genus},
            defaults={"comment": f"Especie {genus_name} {species_name} de la flora demostrativa."},
        )
        species_records.append(species)
        common_name = _active_upsert(
            CommonName,
            using=using,
            lookup={"species": species, "language": spanish, "common_name": common},
            defaults={"dialect": "", "region": CommonName.DEFAULT_REGION},
        )
        _active_upsert(
            Translation,
            using=using,
            lookup={"common_name": common_name, "language": english},
            defaults={"translated_name": translated},
        )
        status = _active_upsert(
            Status,
            using=using,
            lookup={"code": status_code},
            defaults={
                "name": STATUS_NAMES[status_code],
                "description": f"Categoría de conservación {STATUS_NAMES[status_code]}.",
            },
        )
        _active_upsert(
            ConservationStatus,
            using=using,
            lookup={"species": species, "status": status},
            defaults={},
        )

    collectors = [
        _active_upsert(
            Collector,
            using=using,
            lookup={"name": name},
            defaults={"comment": "Colector del catálogo demostrativo del herbario."},
        )
        for name in COLLECTOR_NAMES
    ]

    specimens = []
    marker_icons = ["plant", "flower", "tree", "leaf", "herb"]
    for index in range(1, DEMO_SPECIMEN_COUNT + 1):
        species = species_records[(index - 1) % len(species_records)]
        collector = collectors[(index - 1) % len(collectors)]
        specimen = _active_upsert(
            Specimen,
            using=using,
            lookup={"catalog_code": f"HESP-DEMO-{index:03d}"},
            defaults={
                "is_published": index <= DEMO_SPECIMEN_COUNT - 2,
                "collection_date": date(2026, 7, 15) - timedelta(days=index - 1),
                "collection_number": f"COL-2026-{index:03d}",
                "morphological_description": (
                    f"Ejemplar {index} de {species.genus.name} {species.name}, con estructuras "
                    "vegetativas y reproductivas conservadas para estudio taxonómico."
                ),
                "species": species,
                "collector": collector,
            },
        )
        specimens.append(specimen)
        selected_locations = []
        environments = []
        for order in (1, 2):
            name, latitude, longitude, climate, habitat = _demo_location_data(index, order)
            location = _active_upsert(
                Location,
                using=using,
                lookup={"name": name, "latitude": latitude, "longitude": longitude},
                defaults={
                    "comment": (
                        f"{DEMO_LOCATION_COMMENT_PREFIX} {name}; "
                        f"{specimen.catalog_code}, punto {order}."
                    ),
                },
            )
            climate_record = _active_upsert(
                Climate,
                using=using,
                lookup={"name": climate},
                defaults={},
            )
            habitat_record = _active_upsert(
                Habitat,
                using=using,
                lookup={"name": habitat},
                defaults={},
            )
            _active_upsert(
                ClimateHabitat,
                using=using,
                lookup={"location": location, "climate": climate_record},
                defaults={"habitat": habitat_record},
            )
            selected_locations.append(location)
            environments.append((climate_record, habitat_record))

        specimen.location_links.exclude(location__in=selected_locations).delete()
        specimen.location_links.update(is_primary=False)
        for order, location in enumerate(selected_locations, start=1):
            climate_record, habitat_record = environments[order - 1]
            SpecimenLocation.objects.using(using).update_or_create(
                specimen=specimen,
                location=location,
                defaults={
                    "climate": climate_record,
                    "habitat": habitat_record,
                    "comment": "Punto principal." if order == 1 else "Punto secundario.",
                    "marker_icon": marker_icons[(index + order - 2) % len(marker_icons)],
                    "is_primary": order == 1,
                    "order": order,
                },
            )

    if verbosity >= 1:
        print(
            f"Demo catalog ensured: {len(TAXA)} families, {len(TAXA)} genera, "
            f"{len(TAXA)} species, {len(specimens) * 2} unique locations and "
            f"{len(specimens)} specimens, with no users, roles, collections or images."
        )
    return specimens[0]
