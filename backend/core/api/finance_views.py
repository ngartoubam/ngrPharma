from django.db.models import Sum, F, ExpressionWrapper, DecimalField
from django.db.models.functions import TruncMonth
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions
from drf_spectacular.utils import extend_schema

from core.models import Sale, ProductBatch, Product
from core.permissions import IsAdminOrGerant


# =====================================================
# FINANCIAL DASHBOARD
# =====================================================
class FinanceDashboardView(APIView):
    """
    Dashboard financier global
    """

    permission_classes = [
        permissions.IsAuthenticated,
        IsAdminOrGerant,
    ]

    @extend_schema(
        summary="Financial dashboard",
        responses={
            200: {
                "type": "object",
                "properties": {
                    "revenue": {"type": "number"},
                    "cogs": {"type": "number"},
                    "gross_margin": {"type": "number"},
                    "stock_value": {"type": "number"},
                }
            }
        }
    )
    def get(self, request):
        pharmacy = request.user.pharmacy

        revenue = Sale.objects.filter(
            pharmacy=pharmacy
        ).aggregate(
            total=Sum("total_price")
        )["total"] or 0

        cogs = Sale.objects.filter(
            pharmacy=pharmacy
        ).aggregate(
            total=Sum("cost_total")
        )["total"] or 0

        gross_margin = revenue - cogs

        stock_value = ProductBatch.objects.filter(
            product__pharmacy=pharmacy
        ).aggregate(
            total=Sum(
                ExpressionWrapper(
                    F("quantity") * F("purchase_price"),
                    output_field=DecimalField(max_digits=12, decimal_places=2)
                )
            )
        )["total"] or 0

        return Response({
            "revenue": revenue,
            "cogs": cogs,
            "gross_margin": gross_margin,
            "stock_value": stock_value,
        })


# =====================================================
# MONTHLY FINANCE DASHBOARD
# =====================================================
class MonthlyFinanceView(APIView):
    permission_classes = [
        permissions.IsAuthenticated,
        IsAdminOrGerant,
    ]

    @extend_schema(
        summary="Monthly financial statistics",
        responses={
            200: {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "month": {"type": "string", "format": "date-time"},
                        "revenue": {"type": "number"},
                        "cogs": {"type": "number"},
                        "gross_margin": {"type": "number"},
                    }
                }
            }
        }
    )
    def get(self, request):
        pharmacy = request.user.pharmacy

        data = (
            Sale.objects
            .filter(pharmacy=pharmacy)
            .annotate(month=TruncMonth("created_at"))
            .values("month")
            .annotate(
                revenue=Sum("total_price"),
                cogs=Sum("cost_total")
            )
            .order_by("month")
        )

        results = []
        for item in data:
            revenue = item["revenue"] or 0
            cogs = item["cogs"] or 0

            results.append({
                "month": item["month"],
                "revenue": revenue,
                "cogs": cogs,
                "gross_margin": revenue - cogs
            })

        return Response(results)


# =====================================================
# TOP PROFITABLE PRODUCTS
# =====================================================
class FinanceTopProductsView(APIView):
    permission_classes = [
        permissions.IsAuthenticated,
        IsAdminOrGerant,
    ]

    @extend_schema(
        summary="Top profitable products",
        responses={
            200: {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "product": {"type": "string"},
                        "revenue": {"type": "number"},
                        "cogs": {"type": "number"},
                        "gross_margin": {"type": "number"},
                        "quantity_sold": {"type": "number"},
                    }
                }
            }
        }
    )
    def get(self, request):
        pharmacy = request.user.pharmacy

        products = (
            Sale.objects
            .filter(pharmacy=pharmacy)
            .values("product__name")
            .annotate(
                revenue=Sum("total_price"),
                cogs=Sum("cost_total"),
                quantity_sold=Sum("quantity")
            )
        )

        results = []
        for p in products:
            revenue = p["revenue"] or 0
            cogs = p["cogs"] or 0

            results.append({
                "product": p["product__name"],
                "revenue": revenue,
                "cogs": cogs,
                "gross_margin": revenue - cogs,
                "quantity_sold": p["quantity_sold"] or 0,
            })

        return Response(sorted(results, key=lambda x: x["gross_margin"], reverse=True)[:10])


# =====================================================
# STOCK ROTATION
# =====================================================
class StockRotationView(APIView):
    permission_classes = [
        permissions.IsAuthenticated,
        IsAdminOrGerant,
    ]

    @extend_schema(
        summary="Stock rotation analysis",
        responses={
            200: {
                "type": "object",
                "properties": {
                    "message": {"type": "string"}
                }
            }
        }
    )
    def get(self, request):
        return Response({
            "message": "Stock rotation endpoint working"
        })
