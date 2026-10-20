from __future__ import annotations

import hashlib
import hmac
from typing import Any

from django.conf import settings
from django.db import models
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

PREFIX = "eid"
ALPHABET = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
MASK_32 = (1 << 32) - 1
MASK_64 = (1 << 64) - 1
ROUNDS = 8


class InvalidExternalID(ValueError):
    pass


def model_namespace(model: type[models.Model] | models.Model | Any) -> str:
    model_class = model if isinstance(model, type) else model.__class__
    return model_class._meta.label_lower


def encode_external_id(value: int, *, namespace: str) -> str:
    pk = int(value)
    if pk <= 0:
        raise ValueError("Los identificadores deben ser números enteros positivos.")
    cipher = _feistel(pk, namespace=namespace, decrypt=False)
    mac = _mac(cipher, namespace=namespace)
    return f"{PREFIX}_{_base62_encode(cipher)}_{_base62_encode(mac)}"


def decode_external_id(value: str, *, namespace: str) -> int:
    if not isinstance(value, str):
        raise InvalidExternalID("El identificador externo debe ser una cadena de texto.")
    parts = value.split("_")
    if len(parts) != 3 or parts[0] != PREFIX:
        raise InvalidExternalID("El formato del identificador externo no es válido.")
    try:
        cipher = _base62_decode(parts[1])
        mac = _base62_decode(parts[2])
    except ValueError as exc:
        raise InvalidExternalID("El identificador externo contiene caracteres no válidos.") from exc
    if cipher > MASK_64 or mac >= (1 << 48):
        raise InvalidExternalID("El identificador externo está fuera del rango permitido.")
    expected_mac = _mac(cipher, namespace=namespace)
    if not hmac.compare_digest(mac.to_bytes(6, "big"), expected_mac.to_bytes(6, "big")):
        raise InvalidExternalID("La firma del identificador externo no es válida.")
    pk = _feistel(cipher, namespace=namespace, decrypt=True)
    if pk <= 0:
        raise InvalidExternalID("El valor del identificador externo no es válido.")
    return pk


def decode_query_id(params: dict[str, Any], key: str, model: type[models.Model]) -> int | None:
    value = params.get(key)
    if not value:
        return None
    try:
        return decode_external_id(value, namespace=model_namespace(model))
    except InvalidExternalID as exc:
        raise ValidationError({key: "El identificador proporcionado no es válido."}) from exc


@extend_schema_field(OpenApiTypes.STR)
class EncodedIDField(serializers.Field):
    def __init__(self, *, namespace: str | None = None, **kwargs) -> None:
        kwargs["read_only"] = True
        self.namespace = namespace
        super().__init__(**kwargs)

    def to_representation(self, value) -> str:
        namespace = self.namespace or model_namespace(self.parent.Meta.model)
        pk = value.pk if hasattr(value, "pk") else value
        return encode_external_id(pk, namespace=namespace)


@extend_schema_field(OpenApiTypes.STR)
class EncodedPrimaryKeyRelatedField(serializers.PrimaryKeyRelatedField):
    def __init__(self, *args, model: type[models.Model] | None = None, **kwargs) -> None:
        self.model = model
        super().__init__(*args, **kwargs)

    def to_internal_value(self, data):
        queryset = self.get_queryset()
        if queryset is None:
            self.fail("does_not_exist", pk_value=data)
        namespace = model_namespace(queryset.model)
        try:
            pk = decode_external_id(data, namespace=namespace)
        except InvalidExternalID:
            self.fail("incorrect_type", data_type=type(data).__name__)
        return super().to_internal_value(pk)

    def to_representation(self, value) -> str:
        queryset = self.get_queryset()
        model = self.model or (queryset.model if queryset is not None else value.__class__)
        pk = value.pk if hasattr(value, "pk") else value
        return encode_external_id(pk, namespace=model_namespace(model))


def _key(namespace: str) -> bytes:
    seed = f"{settings.SECRET_KEY}:{namespace}".encode()
    return hashlib.sha256(seed).digest()


def _round_function(value: int, round_number: int, *, namespace: str) -> int:
    payload = value.to_bytes(4, "big") + round_number.to_bytes(1, "big")
    digest = hashlib.blake2s(payload, key=_key(namespace), digest_size=4).digest()
    return int.from_bytes(digest, "big")


def _feistel(value: int, *, namespace: str, decrypt: bool) -> int:
    value &= MASK_64
    left = (value >> 32) & MASK_32
    right = value & MASK_32
    rounds = range(ROUNDS - 1, -1, -1) if decrypt else range(ROUNDS)
    for round_number in rounds:
        if decrypt:
            left, right = right ^ _round_function(left, round_number, namespace=namespace), left
        else:
            left, right = right, left ^ _round_function(right, round_number, namespace=namespace)
    return ((left << 32) | right) & MASK_64


def _mac(cipher: int, *, namespace: str) -> int:
    digest = hmac.new(
        _key(namespace),
        cipher.to_bytes(8, "big"),
        hashlib.sha256,
    ).digest()
    return int.from_bytes(digest[:6], "big")


def _base62_encode(value: int) -> str:
    if value == 0:
        return ALPHABET[0]
    output = []
    while value:
        value, remainder = divmod(value, len(ALPHABET))
        output.append(ALPHABET[remainder])
    return "".join(reversed(output))


def _base62_decode(value: str) -> int:
    result = 0
    for char in value:
        result = result * len(ALPHABET) + ALPHABET.index(char)
    return result
