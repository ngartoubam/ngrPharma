from datetime import date, timedelta
from decimal import Decimal

from django.db.models import Sum, F, DecimalField
from django.db.models.functions import TruncMonth, Coalesce
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions
from drf_spectacular.utils import extend_schema

from core.models import Sale, ProductBatch, SaleBatchConsumption
from core.permissions import IsAdminOrGerant


def _parse_date(value):
    # attend YYYY-MM-DD
    if not value:
        return None
    try:
        y, m, d = value.split("-")
        return date(int(y), int(m), int(d))
    except Exception:
        return None


class FinanceDashboardView(APIView):
    """
    BI Financier (COGS réel) + Stock value + marges
    Query params:
      - date_from=YYYY-MM-DD
      - date_to=YYYY-MM-DD
    """
    permission_classes = [permissions.IsAuthenticated, IsAdminOrGerant]

    @extend_schema(
        summary="Dashboard financier réel (COGS + marge + valeur stock)",
        description="Calcule CA, COGS, marge brute, marge %, valeur stock actuelle basée sur purchase_price des lots.",
    )
    def get(self, request):
        pharmacy = request.user.pharmacy

        date_from = _parse_date(request.GET.get("date_from"))
        date_to = _parse_date(request.GET.get("date_to"))

        if not date_to:
            date_to = date.today()
        if not date_from:
            date_from = date_to - timedelta(days=30)

        sales_qs = Sale.objects.filter(
            pharmacy=pharmacy,
            created_at__date__gte=date_from,
            created_at__date__lte=date_to,
        )

        revenue = sales_qs.aggregate(
            v=Coalesce(Sum("total_price"), Decimal("0.00"))
        )["v"]

        cogs = sales_qs.aggregate(
            v=Coalesce(Sum("cost_total"), Decimal("0.00"))
        )["v"]

        gross_margin = (revenue - cogs)
        margin_pct = (gross_margin / revenue * Decimal("100.0")) if revenue and revenue != 0 else Decimal("0.0")

        # Valeur stock actuelle = Σ (quantity * purchase_price) des lots non expirés
        today = date.today()
        stock_value = ProductBatch.objects.filter(
            product__pharmacy=pharmacy,
            quantity__gt=0,
            expiry_date__gte=today,
        ).aggregate(
            v=Coalesce(
                Sum(F("quantity") * F("purchase_price"), output_field=DecimalField(max_digits=14, decimal_places=2)),
                Decimal("0.00"),
            )
        )["v"]

        return Response({
            "period": {"date_from": str(date_from), "date_to": str(date_to)},
            "kpis": {
                "revenue": str(revenue),
                "cogs": str(cogs),
                "gross_margin": str(gross_margin),
                "margin_pct": str(margin_pct),
                "stock_value_current": str(stock_value),
            }
        })


class FinanceMonthlyView(APIView):
    """
    1️⃣ Dashboard mensuel (CA/COGS/Marge)
    """
    permission_classes = [permissions.IsAuthenticated, IsAdminOrGerant]

    @extend_schema(summary="Série mensuelle CA/COGS/Marge (COGS réel)")
    def get(self, request):
        pharmacy = request.user.pharmacy

        months = int(request.GET.get("months", 12))
        if months < 1:
            months = 12
        end_date = date.today()
        start_date = end_date - timedelta(days=30 * months)

        qs = Sale.objects.filter(
            pharmacy=pharmacy,
            created_at__date__gte=start_date,
            created_at__date__lte=end_date,
        ).annotate(
            month=TruncMonth("created_at")
        ).values("month").annotate(
            revenue=Coalesce(Sum("total_price"), Decimal("0.00")),
            cogs=Coalesce(Sum("cost_total"), Decimal("0.00")),
        ).order_by("month")

        data = []
        for row in qs:
            revenue = row["revenue"]
            cogs = row["cogs"]
            margin = revenue - cogs
            pct = (margin / revenue * Decimal("100.0")) if revenue and revenue != 0 else Decimal("0.0")
            data.append({
                "month": row["month"].date().isoformat(),
                "revenue": str(revenue),
                "cogs": str(cogs),
                "gross_margin": str(margin),
                "margin_pct": str(pct),
            })

        return Response({"months": data})


class FinanceTopProductsView(APIView):
    """
    2️⃣ Top produits rentables
    """
    permission_classes = [permissions.IsAuthenticated, IsAdminOrGerant]

    @extend_schema(summary="Top produits (marge brute) sur une période")
    def get(self, request):
        pharmacy = request.user.pharmacy

        date_from = _parse_date(request.GET.get("date_from"))
        date_to = _parse_date(request.GET.get("date_to"))
        limit = int(request.GET.get("limit", 10))

        if not date_to:
            date_to = date.today()
        if not date_from:
            date_from = date_to - timedelta(days=30)
        if limit < 1:
            limit = 10

        qs = Sale.objects.filter(
            pharmacy=pharmacy,
            created_at__date__gte=date_from,
            created_at__date__lte=date_to,
        ).values(
            "product_id",
            "product__name",
        ).annotate(
            revenue=Coalesce(Sum("total_price"), Decimal("0.00")),
            cogs=Coalesce(Sum("cost_total"), Decimal("0.00")),
            qty=Coalesce(Sum("quantity"), 0),
        ).order_by("-revenue")[:200]  # base

        items = []
        for row in qs:
            margin = row["revenue"] - row["cogs"]
            pct = (margin / row["revenue"] * Decimal("100.0")) if row["revenue"] and row["revenue"] != 0 else Decimal("0.0")
            items.append({
                "product_id": str(row["product_id"]),
                "product_name": row["product__name"],
                "quantity_sold": int(row["qty"]),
                "revenue": str(row["revenue"]),
                "cogs": str(row["cogs"]),
                "gross_margin": str(margin),
                "margin_pct": str(pct),
            })

        items.sort(key=lambda x: Decimal(x["gross_margin"]), reverse=True)
        return Response({
            "period": {"date_from": str(date_from), "date_to": str(date_to)},
            "top": items[:limit]
        })


class StockRotationView(APIView):
    """
    3️⃣ Analyse rotation stock (simple + utile)
    - Stock actuel (qty) / ventes sur période
    - Days of Inventory (approx) : stock_qty / avg_daily_sold_qty
    """
    permission_classes = [permissions.IsAuthenticated, IsAdminOrGerant]

    @extend_schema(summary="Rotation stock (jours de couverture, ventes, stock)")
    def get(self, request):
        pharmacy = request.user.pharmacy
        days = int(request.GET.get("days", 30))
        if days < 1:
            days = 30

        end_date = date.today()
        start_date = end_date - timedelta(days=days)
        today = date.today()

        # ventes par produit (qty)
        sales = Sale.objects.filter(
            pharmacy=pharmacy,
            created_at__date__gte=start_date,
            created_at__date__lte=end_date,
        ).values("product_id", "product__name").annotate(
            sold_qty=Coalesce(Sum("quantity"), 0),
            revenue=Coalesce(Sum("total_price"), Decimal("0.00")),
            cogs=Coalesce(Sum("cost_total"), Decimal("0.00")),
        )

        sales_map = {str(s["product_id"]): s for s in sales}

        # stock actuel par produit (qty + valeur)
        stock = ProductBatch.objects.filter(
            product__pharmacy=pharmacy,
            quantity__gt=0,
            expiry_date__gte=today,
        ).values("product_id", "product__name").annotate(
            stock_qty=Coalesce(Sum("quantity"), 0),
            stock_value=Coalesce(
                Sum(F("quantity") * F("purchase_price"), output_field=DecimalField(max_digits=14, decimal_places=2)),
                Decimal("0.00"),
            )
        )

        items = []
        for st in stock:
            pid = str(st["product_id"])
            sold_qty = int(sales_map.get(pid, {}).get("sold_qty", 0))
            avg_daily = (Decimal(sold_qty) / Decimal(days)) if days else Decimal("0.0")
            days_cover = (Decimal(st["stock_qty"]) / avg_daily) if avg_daily and avg_daily != 0 else None

            revenue = sales_map.get(pid, {}).get("revenue", Decimal("0.00"))
            cogs = sales_map.get(pid, {}).get("cogs", Decimal("0.00"))
            margin = revenue - cogs

            items.append({
                "product_id": pid,
                "product_name": st["product__name"],
                "stock_qty": int(st["stock_qty"]),
                "stock_value": str(st["stock_value"]),
                "sold_qty_period": sold_qty,
                "days": days,
                "days_of_inventory": float(days_cover) if days_cover is not None else None,
                "revenue_period": str(revenue),
                "cogs_period": str(cogs),
                "gross_margin_period": str(margin),
            })

        # Tri: ceux qui tournent vite (jours de couverture faibles) en haut
        items.sort(key=lambda x: (x["days_of_inventory"] is None, x["days_of_inventory"] if x["days_of_inventory"] is not None else 10**9))
        return Response({
            "period": {"days": days, "date_from": str(start_date), "date_to": str(end_date)},
            "items": items
        })
