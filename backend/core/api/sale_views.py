from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions, status
from drf_spectacular.utils import extend_schema

from core.api.sale_serializers import SaleCreateSerializer, SaleListSerializer
from core.models import Sale


class CreateSaleView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(
        request=SaleCreateSerializer,
        responses={201: None},
    )
    def post(self, request):
        serializer = SaleCreateSerializer(
            data=request.data,
            context={"request": request}  # ✅ OBLIGATOIRE
        )
        serializer.is_valid(raise_exception=True)
        sale = serializer.save()

        return Response(
            {
                "sale_id": str(sale.id),
                "total": sale.total_price,
            },
            status=status.HTTP_201_CREATED,
        )

class SaleHistoryView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(
        responses={200: SaleListSerializer(many=True)},
        summary="Historique des ventes par pharmacie",
        description="Retourne toutes les ventes de la pharmacie de l'utilisateur connecté",
    )
    def get(self, request):
        pharmacy = request.user.pharmacy

        sales = (
            Sale.objects
            .filter(pharmacy=pharmacy)
            .select_related("product")
            .order_by("-created_at")
        )

        serializer = SaleListSerializer(sales, many=True)
        return Response(serializer.data)