from __future__ import annotations

from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.throttling import ScopedRateThrottle
from rest_framework.views import APIView

from apps.common.api.serializers import SearchQuerySerializer
from apps.common.services import record_search_query


@extend_schema(tags=["Sistema"], request=SearchQuerySerializer)
class SearchQueryView(APIView):
    permission_classes = [AllowAny]
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "public_searches"

    def post(self, request):
        serializer = SearchQuerySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        search_query = record_search_query(serializer.validated_data["term"])
        return Response(
            {
                "term": search_query.term,
                "search_count": search_query.search_count,
                "has_results": search_query.has_results,
            },
            status=status.HTTP_201_CREATED,
        )
