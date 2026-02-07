from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions, status
from rest_framework_simplejwt.tokens import RefreshToken
from drf_spectacular.utils import extend_schema

from core.models import Pharmacy, CustomUser
from core.api.auth_serializers import PinLoginSerializer


class PinLoginView(APIView):
    permission_classes = [permissions.AllowAny]

    @extend_schema(
        request=PinLoginSerializer,
        responses={
            200: {
                "type": "object",
                "properties": {
                    "access": {"type": "string"},
                    "refresh": {"type": "string"},
                    "user": {
                        "type": "object",
                        "properties": {
                            "id": {"type": "string"},
                            "name": {"type": "string"},
                            "role": {"type": "string"},
                            "pharmacy_id": {"type": "string"},
                        },
                    },
                },
            }
        },
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

        return Response({
            "access": str(refresh.access_token),
            "refresh": str(refresh),
            "user": {
                "id": str(user.id),
                "name": user.name,
                "role": user.role,
                "pharmacy_id": str(pharmacy.id),
            }
        })
