from datetime import datetime
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions, status
from drf_spectacular.utils import extend_schema, OpenApiParameter
from core.permissions import IsAdminOrGerant

from core.api.sale_serializers import SaleCreateSerializer, SaleListSerializer, SaleAuditLogSerializer
from core.models import Sale, SaleAuditLog


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
    permission_classes = [permissions.IsAuthenticated, IsAdminOrGerant,]

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
    
    

class SaleAuditLogListView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(
        responses={200: SaleAuditLogSerializer(many=True)},
        summary="Journal d’audit des ventes",
        description="Historique des ventes bloquées et réussies pour la pharmacie connectée",
    )
    def get(self, request):
        pharmacy = request.user.pharmacy

        audits = (
            SaleAuditLog.objects
            .filter(pharmacy=pharmacy)
            .select_related("product", "user")
            .order_by("-created_at")
        )

        serializer = SaleAuditLogSerializer(audits, many=True)
        return Response(serializer.data)






class SaleAuditLogView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(
        summary="Journal d’audit des ventes",
        description="Historique des ventes bloquées et réussies avec filtres",
        parameters=[
            OpenApiParameter(
                name="reason",
                description="Raison du blocage (expired_stock, insufficient_stock, …)",
                required=False,
                type=str,
            ),
            OpenApiParameter(
                name="product_id",
                description="ID du produit",
                required=False,
                type=str,
            ),
            OpenApiParameter(
                name="date_from",
                description="Date début (YYYY-MM-DD)",
                required=False,
                type=str,
            ),
            OpenApiParameter(
                name="date_to",
                description="Date fin (YYYY-MM-DD)",
                required=False,
                type=str,
            ),
        ],
        responses={200: SaleAuditLogSerializer(many=True)},
    )
    def get(self, request):
        pharmacy = request.user.pharmacy
        qs = SaleAuditLog.objects.filter(pharmacy=pharmacy)

        # 🔹 Filtre par raison
        reason = request.query_params.get("reason")
        if reason:
            qs = qs.filter(reason=reason)

        # 🔹 Filtre par produit
        product_id = request.query_params.get("product_id")
        if product_id:
            qs = qs.filter(product_id=product_id)

        # 🔹 Filtre par date
        date_from = request.query_params.get("date_from")
        if date_from:
            qs = qs.filter(created_at__date__gte=date_from)

        date_to = request.query_params.get("date_to")
        if date_to:
            qs = qs.filter(created_at__date__lte=date_to)

        qs = qs.order_by("-created_at")

        serializer = SaleAuditLogSerializer(qs, many=True)
        return Response(serializer.data)
