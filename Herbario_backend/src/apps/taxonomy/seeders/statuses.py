from __future__ import annotations

from apps.taxonomy.models import Status

STATUSES = [
    {
        "code": "EX",
        "name": "Extinta",
        "description": "No queda ningun individuo vivo conocido.",
    },
    {
        "code": "EW",
        "name": "Extinta en vida silvestre",
        "description": (
            "Solo sobrevive en cultivo, cautiverio o poblaciones fuera de su area natural."
        ),
    },
    {
        "code": "CR",
        "name": "En peligro critico",
        "description": "Riesgo extremadamente alto de extincion en vida silvestre.",
    },
    {
        "code": "EN",
        "name": "En peligro",
        "description": "Riesgo muy alto de extincion en vida silvestre.",
    },
    {
        "code": "VU",
        "name": "Vulnerable",
        "description": "Riesgo alto de extincion en vida silvestre.",
    },
    {
        "code": "NT",
        "name": "Casi amenazada",
        "description": "No esta amenazada actualmente, pero podria estarlo pronto.",
    },
    {
        "code": "LC",
        "name": "Preocupacion menor",
        "description": "Riesgo bajo de extincion segun la evaluacion disponible.",
    },
    {
        "code": "DD",
        "name": "Datos insuficientes",
        "description": "No hay informacion suficiente para evaluar su riesgo.",
    },
    {
        "code": "NE",
        "name": "No evaluada",
        "description": "La especie todavia no ha sido evaluada.",
    },
]


def seed_statuses(*, using: str, verbosity: int = 1, **kwargs) -> None:
    for item in STATUSES:
        Status.all_objects.db_manager(using).update_or_create(
            code=item["code"],
            defaults={
                "name": item["name"],
                "description": item["description"],
                "deleted": False,
                "deleted_at": None,
            },
        )

    if verbosity >= 1:
        print("Taxonomy statuses ensured.")
