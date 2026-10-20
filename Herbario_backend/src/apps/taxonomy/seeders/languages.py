from __future__ import annotations

from apps.taxonomy.models import Language

LANGUAGES = [
    {"code": "es", "name": "Español", "native_name": "Español"},
    {"code": "en", "name": "Inglés", "native_name": "English"},
    {"code": "qu", "name": "Kichwa", "native_name": "Kichwa"},
    {"code": "jiv", "name": "Shuar", "native_name": "Shuar"},
]


def seed_languages(*, using: str, verbosity: int = 1, **kwargs) -> None:
    for item in LANGUAGES:
        Language.all_objects.db_manager(using).update_or_create(
            code=item["code"],
            defaults={
                "name": item["name"],
                "native_name": item["native_name"],
                "deleted": False,
                "deleted_at": None,
            },
        )

    if verbosity >= 1:
        print("Taxonomy languages ensured.")
