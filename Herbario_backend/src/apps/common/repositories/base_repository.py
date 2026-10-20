from __future__ import annotations

from typing import Generic, TypeVar

from django.db import models

ModelT = TypeVar("ModelT", bound=models.Model)


class BaseRepository(Generic[ModelT]):
    model: type[ModelT]

    def __init__(self, model: type[ModelT] | None = None) -> None:
        if model is not None:
            self.model = model

    def get_by_id(self, pk: int) -> ModelT | None:
        return self.model.objects.filter(pk=pk).first()
