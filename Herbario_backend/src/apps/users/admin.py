from django.contrib import admin

from apps.users.models import AuditLog

admin.site.register(AuditLog)
