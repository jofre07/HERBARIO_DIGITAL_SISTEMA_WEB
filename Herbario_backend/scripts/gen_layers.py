"""Generate repository, service, selector, serializer, viewset for simple entities."""
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1] / "src" / "apps"
OPTIONAL_DEFAULT_FIELDS = (
    "comment",
    "climate",
    "habitat",
    "dialect",
    "region",
    "status",
    "collection_type",
    "native_name",
)

SPECS = [
    ("collectors", "collector", "Collector", "name", ["name", "comment"], None),
    (
        "locations",
        "location",
        "Location",
        "name",
        ["name", "latitude", "longitude", "comment"],
        None,
    ),
    (
        "locations",
        "climate_habitat",
        "ClimateHabitat",
        None,
        ["location", "climate", "habitat"],
        [("location", "locations.Location", "Location not found.")],
    ),
    ("taxonomy", "family", "Family", "name", ["name", "comment"], None),
    (
        "taxonomy",
        "genus",
        "Genus",
        None,
        ["name", "family", "comment"],
        [("family", "taxonomy.Family", "Family not found.")],
    ),
    (
        "taxonomy",
        "species",
        "Species",
        None,
        ["name", "genus", "comment"],
        [("genus", "taxonomy.Genus", "Genus not found.")],
    ),
    ("taxonomy", "language", "Language", "code", ["code", "name", "native_name"], None),
    (
        "taxonomy",
        "common_name",
        "CommonName",
        None,
        ["species", "language", "common_name", "dialect", "region"],
        [
            ("species", "taxonomy.Species", "Species not found."),
            ("language", "taxonomy.Language", "Language not found."),
        ],
    ),
    (
        "taxonomy",
        "translation",
        "Translation",
        None,
        ["common_name", "language", "translated_name"],
        [
            ("common_name", "taxonomy.CommonName", "Common name not found."),
            ("language", "taxonomy.Language", "Language not found."),
        ],
    ),
    (
        "taxonomy",
        "conservation_status",
        "ConservationStatus",
        None,
        ["species", "status"],
        [("species", "taxonomy.Species", "Species not found.")],
    ),
]


def w(path: str, content: str) -> None:
    p = ROOT / path
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content, encoding="utf-8")


def gen_repo(app: str, snake: str, entity: str, unique: str | None) -> str:
    lines = [
        "from __future__ import annotations",
        "",
        "from apps.common.repositories.base_repository import BaseRepository",
        f"from apps.{app}.models import {entity}",
        "",
        "",
        f"class {entity}Repository(BaseRepository[{entity}]):",
        f"    model = {entity}",
        "",
        f"    def create(self, **data) -> {entity}:",
        f"        return {entity}.objects.create(**data)",
        "",
        f"    def save(self, instance: {entity}) -> {entity}:",
        "        instance.save()",
        "        return instance",
        "",
        f"    def soft_delete(self, instance: {entity}) -> None:",
        "        instance.soft_delete()",
    ]
    if unique:
        lines += [
            "",
            f"    def get_by_{unique}(self, {unique}: str) -> {entity} | None:",
            f"        return {entity}.objects.filter({unique}={unique}).first()",
        ]
    return "\n".join(lines) + "\n"


def gen_service(
    app: str,
    snake: str,
    entity: str,
    unique: str | None,
    write_fields: list[str],
    fks: list | None,
) -> str:
    repo = f"{entity}Repository"
    lines = [
        "from __future__ import annotations",
        "",
        "from typing import Any",
        "",
        "from django.db import transaction",
        "",
        "from apps.common.exceptions import ConflictError, NotFoundError",
        f"from apps.{app}.models import {entity}",
        f"from apps.{app}.repositories import {repo}",
    ]
    for _fk_field, model_path, _ in fks or []:
        if "get_user_model" in model_path:
            lines.append("from django.contrib.auth import get_user_model")
        else:
            mod, cls = model_path.rsplit(".", 1)
            lines.append(f"from apps.{mod}.models import {cls}")

    lines += [
        "",
        "",
        f"class {entity}Service:",
        f"    def __init__(self, repository: {repo} | None = None) -> None:",
        f"        self.repository = repository or {repo}()",
        "",
    ]

    # resolvers
    for fk_field, model_path, _msg in fks or []:
        cls = "get_user_model()" if "get_user_model" in model_path else model_path.split(".")[-1]
        model_ref = "get_user_model()" if "get_user_model" in model_path else cls
        lines += [
            f"    def _resolve_{fk_field}(self, value):",
            "        if value is None:",
            "            return None",
            "        if hasattr(value, 'pk'):",
            "            return value",
            f"        return {model_ref}.objects.filter(pk=value).first()",
            "",
        ]

    lines += [
        "    @transaction.atomic",
        "    def create(self, *, data: dict[str, Any]) -> " + entity + ":",
    ]
    if unique:
        lines.append(f'        if self.repository.get_by_{unique}(data["{unique}"]):')
        lines.append(f'            raise ConflictError("{entity} already exists.")')
    for fk_field, _, msg in fks or []:
        lines += [
            f'        {fk_field} = self._resolve_{fk_field}(data.get("{fk_field}"))',
            f'        if data.get("{fk_field}") is not None and {fk_field} is None:',
            f'            raise NotFoundError("{msg}")',
        ]
    # build create kwargs properly
    kwargs_lines = []
    for f in write_fields:
        if fks and f in [x[0] for x in fks]:
            kwargs_lines.append(f"{f}={f}")
        elif f in OPTIONAL_DEFAULT_FIELDS:
            kwargs_lines.append(f'{f}=data.get("{f}", "")')
        else:
            kwargs_lines.append(f'{f}=data["{f}"]')
    lines.append(f"        return self.repository.create({', '.join(kwargs_lines)})")

    lines += [
        "",
        "    @transaction.atomic",
        f"    def update(self, instance: {entity}, *, data: dict[str, Any]) -> {entity}:",
    ]
    if unique:
        lines += [
            f'        if "{unique}" in data and data["{unique}"] != getattr(instance, "{unique}"):',
            f'            existing = self.repository.get_by_{unique}(data["{unique}"])',
            "            if existing and existing.pk != instance.pk:",
            f'                raise ConflictError("{entity} already exists.")',
            f'            instance.{unique} = data["{unique}"]',
        ]
    for f in write_fields:
        if f == unique:
            continue
        if fks and f == fks[0][0]:
            continue
        if f in (*OPTIONAL_DEFAULT_FIELDS, "description"):
            lines.append(f'        if "{f}" in data:')
            lines.append(f'            instance.{f} = data["{f}"]')
        elif fks and any(f == x[0] for x in fks):
            pass
    for fk_field, _, msg in fks or []:
        lines += [
            f'        if "{fk_field}" in data:',
            f'            resolved = self._resolve_{fk_field}(data["{fk_field}"])',
            f"            if data[\"{fk_field}\"] is not None and resolved is None:",
            f'                raise NotFoundError("{msg}")',
            f"            instance.{fk_field} = resolved",
        ]
    for f in write_fields:
        if f in (unique, "comment") or (fks and f in [x[0] for x in fks]):
            if f not in (unique,) and not (fks and f in [x[0] for x in fks]):
                pass
        elif f not in (unique,) and not (fks and f in [x[0] for x in fks]):
            lines.append(f'        if "{f}" in data:')
            lines.append(f'            instance.{f} = data["{f}"]')

    lines += [
        "",
        "        return self.repository.save(instance)",
        "",
        "    @transaction.atomic",
        f"    def soft_delete(self, instance: {entity}) -> None:",
        "        self.repository.soft_delete(instance)",
        "",
    ]
    return "\n".join(lines)


# Run only repo + selector + serializer + viewset with simpler approach
for app, snake, entity, unique, _write_fields, _fks in SPECS:
    w(f"{app}/repositories/{snake}_repository.py", gen_repo(app, snake, entity, unique))
    print(app, snake, "repo ok")

print("finished")
