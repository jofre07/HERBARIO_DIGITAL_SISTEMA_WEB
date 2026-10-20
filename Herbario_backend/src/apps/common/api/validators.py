from __future__ import annotations

import re

from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _


def validate_letters_spaces(value: str) -> None:
    if not re.fullmatch(r"[A-Za-zÁÉÍÓÚÜÑáéíóúüñ\s]+", value):
        raise ValidationError(
            _("Solo se permiten letras y espacios (sin números ni caracteres especiales).")
        )


def validate_alphanumeric_hyphen(value: str) -> None:
    if not re.fullmatch(r"[A-Za-zÁÉÍÓÚÜÑáéíóúüñ0-9\s\-]+", value):
        raise ValidationError(
            _("Solo se permiten letras, números, espacios y guiones.")
        )


def validate_no_html(value: str) -> None:
    if re.search(r"<[^>]*>", value):
        raise ValidationError(
            _("No se permiten etiquetas HTML.")
        )
