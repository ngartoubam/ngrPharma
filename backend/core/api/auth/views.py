# backend/core/api/auth/views.py

from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from rest_framework import permissions, status
from rest_framework_simplejwt.tokens import RefreshToken
from drf_spectacular.utils import extend_schema

from django.contrib.auth import authenticate
from django.utils import timezone

from core.models import Pharmacy, CustomUser
from .serializers import (
    PinLoginSerializer,
    AdminLoginSerializer,
)


# =========================================================
# 🔐 UTILITAIRE JWT
# =========================================================
def generate_tokens_for_user(user, pharmacy=None, is_saas_admin=False):

    refresh = RefreshToken.for_user(user)

    refresh["role"] = user.role
    refresh["is_saas_admin"] = is_saas_admin
    refresh["pharmacy_id"] = str(pharmacy.id) if pharmacy else None

    if pharmacy:
        refresh["subscription_status"] = pharmacy.subscription_status
        refresh["is_active"] = pharmacy.is_active

    return {
        "access": str(refresh.access_token),
        "refresh": str(refresh),
    }


# =========================================================
# PIN LOGIN (PHARMACIE / CAISSE)
# =========================================================
class PinLoginView(GenericAPIView):

    permission_classes = [permissions.AllowAny]
    serializer_class = PinLoginSerializer

    @extend_schema(
        request=PinLoginSerializer,
        summary="PIN Login (Pharmacie / Caisse)",
    )
    def post(self, request):

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        pharmacy_id = serializer.validated_data["pharmacy_id"]
        pin = serializer.validated_data["pin"]

        try:
            pharmacy = Pharmacy.objects.get(id=pharmacy_id)
        except Pharmacy.DoesNotExist:
            return Response(
                {"detail": "Invalid pharmacy"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user = CustomUser.objects.filter(
            pharmacy=pharmacy,
            is_active=True
        ).first()

        if not user or not user.check_pin(pin):
            return Response(
                {"detail": "Invalid PIN"},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        tokens = generate_tokens_for_user(
            user=user,
            pharmacy=pharmacy,
            is_saas_admin=False
        )

        return Response({
            **tokens,
            "user": {
                "id": str(user.id),
                "name": user.name,
                "role": user.role,
                "is_saas_admin": False,
                "subscription_status": pharmacy.subscription_status,
                "subscription_active": pharmacy.has_active_subscription(),
                "pharmacy": {
                    "id": str(pharmacy.id),
                    "name": pharmacy.name,
                    "plan": pharmacy.plan,
                    "subscription_status": pharmacy.subscription_status,
                    "current_period_end": pharmacy.current_period_end,
                }
            }
        })


# =========================================================
# SAAS ADMIN LOGIN
# =========================================================
class AdminLoginView(GenericAPIView):

    permission_classes = [permissions.AllowAny]
    serializer_class = AdminLoginSerializer

    @extend_schema(
        request=AdminLoginSerializer,
        summary="SaaS Admin Login (Email / Password)",
    )
    def post(self, request):

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data["email"]
        password = serializer.validated_data["password"]

        user = authenticate(request, username=email, password=password)

        if not user:
            return Response(
                {"detail": "Invalid credentials"},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        if not user.is_active:
            return Response(
                {"detail": "Account disabled"},
                status=status.HTTP_403_FORBIDDEN,
            )

        if not getattr(user, "is_saas_admin", False):
            return Response(
                {"detail": "Not authorized as SaaS Admin"},
                status=status.HTTP_403_FORBIDDEN,
            )

        tokens = generate_tokens_for_user(
            user=user,
            pharmacy=None,
            is_saas_admin=True
        )

        return Response({
            **tokens,
            "user": {
                "id": str(user.id),
                "email": user.email,
                "name": user.name,
                "role": user.role,
                "is_saas_admin": True,
                "pharmacy": None,
            }
        })