from drf_spectacular.utils import extend_schema, inline_serializer
from rest_framework import serializers
from rest_framework.response import Response
from rest_framework.views import APIView


@extend_schema(
    tags=["Sistema"],
    responses=inline_serializer(
        name="HealthCheckResponse",
        fields={
            "status": serializers.CharField(),
            "service": serializers.CharField(),
        },
    ),
)
class HealthCheckView(APIView):
    def get(self, request):
        return Response({"status": "ok", "service": "herbario-api"})
