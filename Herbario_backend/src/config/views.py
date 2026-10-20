from __future__ import annotations

from drf_spectacular.utils import extend_schema
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView


@extend_schema(tags=["Documentacion"])
class SchemaView(SpectacularAPIView):
    skip_standard_response = True


@extend_schema(tags=["Documentacion"])
class SwaggerDocsView(SpectacularSwaggerView):
    skip_standard_response = True
