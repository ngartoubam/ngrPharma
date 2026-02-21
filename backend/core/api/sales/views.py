# backend/core/api/sales/views.py

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions, status
from drf_spectacular.utils import extend_schema, OpenApiParameter

from core.permissions import IsAdminOrGerant
from core.models import Sale, SaleAuditLog

from .serializers import (
    SaleCreateSerializer,
    SaleListSerializer,
    SaleAuditLogSerializer,
)


# ======================================================
# CREATE SALE
# ======================================================
class CreateSaleView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(
        request=SaleCreateSerializer,
        responses={201: None},
    )
    def post(self, request):
        serializer = SaleCreateSerializer(
            data=request.data,
            context={"request": request}
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


# ======================================================
# SALE HISTORY
# ======================================================
class SaleHistoryView(APIView):
    permission_classes = [permissions.IsAuthenticated, IsAdminOrGerant]

    @extend_schema(
        responses={200: SaleListSerializer(many=True)},
        summary="Historique des ventes",
        description="Retourne toutes les ventes de la pharmacie connectée",
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


# ======================================================
# SALE AUDIT LOG (WITH FILTERS)
# ======================================================
class SaleAuditLogView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(
        summary="Journal d’audit des ventes",
        description="Historique des ventes bloquées et réussies avec filtres",
        parameters=[
            OpenApiParameter(name="reason", type=str, required=False),
            OpenApiParameter(name="product_id", type=str, required=False),
            OpenApiParameter(name="date_from", type=str, required=False),
            OpenApiParameter(name="date_to", type=str, required=False),
        ],
        responses={200: SaleAuditLogSerializer(many=True)},
    )
    def get(self, request):
        pharmacy = request.user.pharmacy
        qs = SaleAuditLog.objects.filter(pharmacy=pharmacy)

        reason = request.query_params.get("reason")
        if reason:
            qs = qs.filter(reason=reason)

        product_id = request.query_params.get("product_id")
        if product_id:
            qs = qs.filter(product_id=product_id)

        date_from = request.query_params.get("date_from")
        if date_from:
            qs = qs.filter(created_at__date__gte=date_from)

        date_to = request.query_params.get("date_to")
        if date_to:
            qs = qs.filter(created_at__date__lte=date_to)

        qs = qs.order_by("-created_at")

        serializer = SaleAuditLogSerializer(qs, many=True)
        return Response(serializer.data)