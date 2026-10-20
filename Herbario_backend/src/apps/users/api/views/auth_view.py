from __future__ import annotations

from drf_spectacular.utils import extend_schema
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from apps.users.api.serializers.auth_serializer import LoginTokenSerializer


@extend_schema(tags=["Autenticacion"])
class LoginTokenView(TokenObtainPairView):
    serializer_class = LoginTokenSerializer


@extend_schema(tags=["Autenticacion"])
class RefreshTokenView(TokenRefreshView):
    pass
