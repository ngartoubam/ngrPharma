from datetime import datetime

from django.db.models import Sum, F, DecimalField, ExpressionWrapper
from django.db.models.functions import Coalesce
from django.utils.timezone import now
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions
from drf_spectacular.utils import extend_schema

from core.permissions import IsAdminOrGerant
from core.models import Sale, ProductBatch


def _parse_date(value: str):
    """
    Attend YYYY-MM-DD. Retourne un date ou None.
    """
    if not value:
        return None
    try:
        return datetime.strptime(value, "%Y-%m-%d").date()
    except ValueError:
        return None


class DashboardFinanceView(APIView):
    """
    Dashboard financier avancé : ventes, marges estimées, valeur stock.
    """
    permission_classes = [permissions.IsAuthenticated, IsAdminOrGerant]

    @extend_schema(
        summary="Dashboard financier (marges + valeur stock)",
        description=(
            "Retourne CA, COGS estimé, marge brute, taux de marge, "
            "et valeur du stock (coût + vente). "
            "Filtres: date_from=YYYY-MM-DD, date_to=YYYY-MM-DD"
        ),
    )
    def get(self, request):
        pharmacy = request.user.pharmacy

        date_from = _parse_date(request.GET.get("date_from"))
        date_to = _parse_date(request.GET.get("date_to"))

        # -------------------------
        # SALES (revenu / marge)
        # -------------------------
        sales_qs = Sale.objects.filter(pharmacy=pharmacy)

        if date_from:
            sales_qs = sales_qs.filter(created_at__date__gte=date_from)
        if date_to:
            sales_qs = sales_qs.filter(created_at__date__lte=date_to)

        revenue = sales_qs.aggregate(
            total=Coalesce(Sum("total_price"), 0)
        )["total"]

        # COGS estimé = quantity * product.purchase_price (coût courant)
        cogs_expr = ExpressionWrapper(
            F("quantity") * F("product__purchase_price"),
            output_field=DecimalField(max_digits=14, decimal_places=2),
        )
        cogs = sales_qs.aggregate(
            total=Coalesce(Sum(cogs_expr), 0)
        )["total"]

        gross_margin = revenue - cogs
        margin_rate = (gross_margin / revenue) if revenue else 0

        # -------------------------
        # STOCK VALUE (non expiré)
        # -------------------------
        today = now().date()
        batches_qs = ProductBatch.objects.filter(
            product__pharmacy=pharmacy,
            quantity__gt=0,
            expiry_date__gte=today,   # stock "valide"
        )

        stock_qty = batches_qs.aggregate(
            total=Coalesce(Sum("quantity"), 0)
        )["total"]

        stock_cost_expr = ExpressionWrapper(
            F("quantity") * F("product__purchase_price"),
            output_field=DecimalField(max_digits=14, decimal_places=2),
        )
        stock_sale_expr = ExpressionWrapper(
            F("quantity") * F("product__unit_price"),
            output_field=DecimalField(max_digits=14, decimal_places=2),
        )

        stock_cost_value = batches_qs.aggregate(
            total=Coalesce(Sum(stock_cost_expr), 0)
        )["total"]

        stock_sale_value = batches_qs.aggregate(
            total=Coalesce(Sum(stock_sale_expr), 0)
        )["total"]

        payload = {
            "filters": {
                "date_from": str(date_from) if date_from else None,
                "date_to": str(date_to) if date_to else None,
            },
            "sales": {
                "revenue": str(revenue),
                "cogs_estimated": str(cogs),
                "gross_margin": str(gross_margin),
                "margin_rate": float(margin_rate),
            },
            "stock": {
                "stock_quantity": int(stock_qty),
                "stock_cost_value": str(stock_cost_value),
                "stock_sale_value": str(stock_sale_value),
            },
        }

        return Response(payload)
