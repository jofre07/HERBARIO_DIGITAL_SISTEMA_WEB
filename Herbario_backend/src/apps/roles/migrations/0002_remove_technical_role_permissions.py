from django.db import migrations


BUSINESS_PERMISSION_APPS = (
    "collections_app",
    "collectors",
    "locations",
    "media",
    "specimens",
    "taxonomy",
    "users",
)

AUTH_PERMISSION_MODELS = ("group", "user")


def remove_technical_role_permissions(apps, schema_editor):
    Permission = apps.get_model("auth", "Permission")
    Group = apps.get_model("auth", "Group")
    allowed_permission_ids = Permission.objects.filter(
        content_type__app_label__in=BUSINESS_PERMISSION_APPS
    ).values_list("id", flat=True)
    allowed_auth_permission_ids = Permission.objects.filter(
        content_type__app_label="auth",
        content_type__model__in=AUTH_PERMISSION_MODELS,
    ).values_list("id", flat=True)
    Group.permissions.through.objects.exclude(
        permission_id__in=[*allowed_permission_ids, *allowed_auth_permission_ids]
    ).delete()


class Migration(migrations.Migration):
    dependencies = [("roles", "0001_initial")]

    operations = [
        migrations.RunPython(
            remove_technical_role_permissions,
            reverse_code=migrations.RunPython.noop,
        )
    ]
