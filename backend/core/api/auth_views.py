# backend/core/api/auth_views.py

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions, status
from rest_framework_simplejwt.tokens import RefreshToken
from drf_spectacular.utils import extend_schema

from django.contrib.auth import authenticate

from core.models import Pharmacy, CustomUser
from core.api.auth_serializers import (
    PinLoginSerializer,
    EmailLoginSerializer
)


# =========================================================
# PIN LOGIN (MODE CAISSE)
# =========================================================
class PinLoginView(APIView):
    permission_classes = [permissions.AllowAny]

    @extend_schema(
        request=PinLoginSerializer,
        summary="PIN Login (Mode Caisse)",
    )
    def post(self, request):
        serializer = PinLoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        try:
            pharmacy = Pharmacy.objects.get(id=data["pharmacy_id"])
        except Pharmacy.DoesNotExist:
            return Response(
                {"detail": "Invalid pharmacy"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user = CustomUser.objects.filter(
            pharmacy=pharmacy,
            is_active=True
        ).first()

        if not user or not user.check_pin(data["pin"]):
            return Response(
                {"detail": "Invalid PIN"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        refresh = RefreshToken.for_user(user)
        refresh["pharmacy_id"] = str(pharmacy.id)
        refresh["role"] = user.role
        refresh["is_saas_admin"] = getattr(user, "is_saas_admin", False)

        return Response({
            "access": str(refresh.access_token),
            "refresh": str(refresh),
            "user": {
                "id": str(user.id),
                "name": user.name,
                "role": user.role,
                "pharmacy_id": str(pharmacy.id),
                "is_saas_admin": getattr(user, "is_saas_admin", False),
            }
        })


# =========================================================
# EMAIL / PASSWORD LOGIN (SaaS MULTI-PHARMACY)
# =========================================================
class EmailLoginView(APIView):
    permission_classes = [permissions.AllowAny]

    @extend_schema(
        request=EmailLoginSerializer,
        summary="SaaS Login (Email / Password)",
    )
    def post(self, request):
        serializer = EmailLoginSerializer(data=request.data)
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

        refresh = RefreshToken.for_user(user)

        refresh["role"] = user.role
        refresh["is_saas_admin"] = getattr(user, "is_saas_admin", False)
        refresh["pharmacy_id"] = (
            str(user.pharmacy.id) if user.pharmacy else None
        )

        return Response({
            "access": str(refresh.access_token),
            "refresh": str(refresh),
            "user": {
                "id": str(user.id),
                "email": user.email,
                "name": user.name,
                "role": user.role,
                "is_saas_admin": getattr(user, "is_saas_admin", False),
                "pharmacy": {
                    "id": str(user.pharmacy.id),
                    "name": user.pharmacy.name,
                } if user.pharmacy else None,
            }
        })
