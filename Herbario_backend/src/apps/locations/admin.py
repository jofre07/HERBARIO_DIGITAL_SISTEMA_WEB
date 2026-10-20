from django.contrib import admin

from apps.locations.models import Climate, ClimateHabitat, Habitat, Location

admin.site.register(Location)
admin.site.register(ClimateHabitat)
admin.site.register(Climate)
admin.site.register(Habitat)
