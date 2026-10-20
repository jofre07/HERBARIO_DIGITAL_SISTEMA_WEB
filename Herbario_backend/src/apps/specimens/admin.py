from django.contrib import admin

from .models import Specimen, SpecimenLocation

admin.site.register(Specimen)
admin.site.register(SpecimenLocation)
