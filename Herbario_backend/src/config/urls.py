from django.conf import settings
from django.conf.urls.static import static
from django.urls import include, path

from apps.users.api.views import LoginTokenView, RefreshTokenView
from config.views import SchemaView, SwaggerDocsView

urlpatterns = [
    path("api/schema/", SchemaView.as_view(), name="schema"),
    path("api/docs/", SwaggerDocsView.as_view(url_name="schema"), name="swagger-ui"),
    path("api/token/", LoginTokenView.as_view(), name="token_obtain_pair"),
    path("api/token/refresh/", RefreshTokenView.as_view(), name="token_refresh"),
    path("api/", include("apps.common.urls")),
    path("api/public/", include("apps.common.public_urls")),
    path("api/users/", include("apps.users.urls")),
    path("api/roles/", include("apps.roles.urls")),
    path("api/taxonomy/", include("apps.taxonomy.urls")),
    path("api/collectors/", include("apps.collectors.urls")),
    path("api/locations/", include("apps.locations.urls")),
    path("api/specimens/", include("apps.specimens.urls")),
    path("api/media/", include("apps.media.urls")),
    path("api/collections/", include("apps.collections_app.urls")),
    path("api/content/", include("apps.site_content.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
