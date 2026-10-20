from django.contrib import admin

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

admin.site.register(Family)
admin.site.register(Genus)
admin.site.register(Language)
admin.site.register(Species)
admin.site.register(Status)
admin.site.register(CommonName)
admin.site.register(Translation)
admin.site.register(ConservationStatus)
