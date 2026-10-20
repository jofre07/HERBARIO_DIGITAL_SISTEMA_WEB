from drf_spectacular.utils import extend_schema
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.site_content.api.permissions import AboutPageContentPermission
from apps.site_content.api.serializers import AboutPageContentSerializer
from apps.site_content.models import AboutPageContent


def get_about_content() -> AboutPageContent:
    content, _ = AboutPageContent.objects.get_or_create(pk=1)
    return content


@extend_schema(tags=["Contenido"])
class PublicAboutPageContentView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        serializer = AboutPageContentSerializer(get_about_content(), context={"request": request})
        return Response(serializer.data)


@extend_schema(tags=["Contenido"])
class AboutPageContentAdminView(APIView):
    permission_classes = [IsAuthenticated, AboutPageContentPermission]
    parser_classes = [JSONParser, MultiPartParser, FormParser]

    def get(self, request):
        serializer = AboutPageContentSerializer(get_about_content(), context={"request": request})
        return Response(serializer.data)

    def patch(self, request):
        content = get_about_content()
        serializer = AboutPageContentSerializer(
            content,
            data=request.data,
            partial=True,
            context={"request": request},
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)
