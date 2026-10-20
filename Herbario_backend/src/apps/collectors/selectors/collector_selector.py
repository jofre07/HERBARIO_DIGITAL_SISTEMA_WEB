from __future__ import annotations

from django.db.models import QuerySet

from apps.collectors.models import Collector


def list_collectors_for_api() -> QuerySet[Collector]:
    return Collector.objects.order_by("name")
