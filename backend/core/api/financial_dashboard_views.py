from django.db.models import Sum, F, DecimalField
from django.db.models.functions import Coalesce
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions

from core.models import Sale, ProductBatch
from core.permissions import IsAdminOrGerant


class FinancialDashboardView(APIView):
    """
    Dashboard financier réel :
    - Chiffre d'affaires
    - Coût des ventes (COGS FIFO réel)
    - Marge brute
    - Valeur actuelle du stock
    """
    permission_classes = [
        permissions.IsAuthenticated,
        IsAdminOrGerant
    ]

    def get(self, request):
        pharmacy = request.user.pharmacy

        # ===============================
        # 💰 CHIFFRE D'AFFAIRES
        # ===============================
        total_revenue = (
            Sale.objects
            .filter(pharmacy=pharmacy)
            .aggregate(total=Coalesce(Sum("total_price"), 0))["total"]
        )

        # ===============================
        # 📉 COÛT DES VENTES (COGS)
        # ===============================
        total_cogs = (
            Sale.objects
            .filter(pharmacy=pharmacy)
            .aggregate(total=Coalesce(Sum("cost_total"), 0))["total"]
        )

        # ===============================
        # 📈 MARGE BRUTE
        # ===============================
        gross_margin = total_revenue - total_cogs

        margin_percentage = 0
        if total_revenue > 0:
            margin_percentage = (gross_margin / total_revenue) * 100

        # ===============================
        # 📦 VALEUR ACTUELLE DU STOCK
        # ===============================
        stock_value = (
            ProductBatch.objects
            .filter(product__pharmacy=pharmacy, quantity__gt=0)
            .aggregate(
                total=Coalesce(
                    Sum(F("quantity") * F("purchase_price"), output_field=DecimalField()),
                    0
                )
            )["total"]
        )

        return Response({
            "revenue": total_revenue,
            "cogs": total_cogs,
            "gross_margin": gross_margin,
            "margin_percentage": round(margin_percentage, 2),
            "stock_value": stock_value,
        })
