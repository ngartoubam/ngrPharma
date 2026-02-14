from django.db import models
from django.utils.timezone import now
from datetime import timedelta

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions
from drf_spectacular.utils import extend_schema

from core.models import Product, ProductBatch, SaleAuditLog
from core.permissions import IsAdminOrGerant


class DashboardAlertsView(APIView):
    """
    Dashboard global des alertes (stock, expiration, ventes bloquées)
    """
    permission_classes = [permissions.IsAuthenticated, IsAdminOrGerant]

    @extend_schema(
        summary="Dashboard alertes",
        description="Retourne les alertes clés pour la pharmacie connectée",
        responses={
            200: {
                "type": "object",
                "properties": {
                    "low_stock_products": {"type": "integer"},
                    "expired_batches": {"type": "integer"},
                    "expiring_soon_batches": {"type": "integer"},
                    "blocked_sales_last_7_days": {"type": "integer"},
                }
            }
        }
    )
    def get(self, request):
        pharmacy = request.user.pharmacy
        today = now().date()
        expiry_limit = today + timedelta(days=30)

        # 🔔 Produits stock bas
        low_stock_count = (
            Product.objects
            .filter(
                pharmacy=pharmacy,
                is_active=True,
                batches__quantity__gt=0
            )
            .annotate(stock=models.Sum("batches__quantity"))
            .filter(stock__lte=models.F("min_stock_level"))
            .distinct()
            .count()
        )

        # ⏰ Lots expirés
        expired_batches_count = ProductBatch.objects.filter(
            product__pharmacy=pharmacy,
            quantity__gt=0,
            expiry_date__lt=today
        ).count()

        # ⚠️ Lots proches expiration
        expiring_soon_batches_count = ProductBatch.objects.filter(
            product__pharmacy=pharmacy,
            quantity__gt=0,
            expiry_date__range=(today, expiry_limit)
        ).count()

        # 🚫 Ventes bloquées (7 jours)
        blocked_sales_count = SaleAuditLog.objects.filter(
            pharmacy=pharmacy,
            created_at__date__gte=today - timedelta(days=7)
        ).count()

        return Response({
            "low_stock_products": low_stock_count,
            "expired_batches": expired_batches_count,
            "expiring_soon_batches": expiring_soon_batches_count,
            "blocked_sales_last_7_days": blocked_sales_count,
        })
