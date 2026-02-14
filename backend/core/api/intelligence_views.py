from datetime import timedelta
from django.db.models import Sum, Count
from django.utils.timezone import now

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions, serializers
from drf_spectacular.utils import extend_schema

from core.models import Sale, Product, ProductBatch
from core.permissions import IsAdminOrGerant


# =====================================================
# RESPONSE SERIALIZER (Swagger Fix)
# =====================================================

class IntelligenceResponseSerializer(serializers.Serializer):
    period = serializers.DictField()
    financial_health_score = serializers.DictField()
    stock_health_index = serializers.DictField()
    underperforming_products = serializers.ListField()
    sales_forecast_7d = serializers.DictField()
    alert_intelligence = serializers.ListField()


# =====================================================
# INTELLIGENCE VIEW
# =====================================================

class IntelligenceView(APIView):
    """
    Intelligence endpoint (BI):
    1) Financial Health Score
    2) Stock Health Index
    3) Underperforming products
    4) Sales forecast 7 days (mini IA baseline)
    5) Alert intelligence
    """

    permission_classes = [permissions.IsAuthenticated, IsAdminOrGerant]
    serializer_class = IntelligenceResponseSerializer

    @extend_schema(
        summary="BI Intelligence (score, stock index, underperformers, forecast, alerts)",
        responses=IntelligenceResponseSerializer
    )
    def get(self, request):

        pharmacy = request.user.pharmacy
        today = now().date()

        # -------------------------
        # PERIODS
        # -------------------------
        current_start = today - timedelta(days=29)
        current_end = today
        prev_start = current_start - timedelta(days=30)
        prev_end = current_start - timedelta(days=1)

        # -------------------------
        # SALES AGG (CURRENT / PREV)
        # -------------------------
        current_sales = Sale.objects.filter(
            pharmacy=pharmacy,
            created_at__date__gte=current_start,
            created_at__date__lte=current_end,
        )
        prev_sales = Sale.objects.filter(
            pharmacy=pharmacy,
            created_at__date__gte=prev_start,
            created_at__date__lte=prev_end,
        )

        cur = current_sales.aggregate(
            revenue=Sum("total_price"),
            cogs=Sum("cost_total"),
            cnt=Count("id"),
        )
        prv = prev_sales.aggregate(
            revenue=Sum("total_price"),
            cogs=Sum("cost_total"),
            cnt=Count("id"),
        )

        cur_revenue = cur["revenue"] or 0
        cur_cogs = cur["cogs"] or 0
        cur_cnt = cur["cnt"] or 0
        cur_margin = cur_revenue - cur_cogs
        cur_margin_pct = (cur_margin / cur_revenue * 100) if cur_revenue else 0

        prev_revenue = prv["revenue"] or 0
        prev_margin = (prv["revenue"] or 0) - (prv["cogs"] or 0)

        def pct_change(current, previous):
            if previous == 0:
                return 100 if current > 0 else 0
            return ((current - previous) / previous) * 100

        revenue_change_pct = pct_change(cur_revenue, prev_revenue)
        margin_change_pct = pct_change(cur_margin, prev_margin)

        # -------------------------
        # FINANCIAL HEALTH SCORE
        # -------------------------
        score = 0

        if revenue_change_pct >= 10:
            score += 30
        elif revenue_change_pct >= 0:
            score += 20
        elif revenue_change_pct >= -10:
            score += 10

        if cur_margin_pct >= 30:
            score += 30
        elif cur_margin_pct >= 20:
            score += 20
        elif cur_margin_pct >= 10:
            score += 10

        anomaly = revenue_change_pct < -30
        score += 20 if not anomaly else 5

        if cur_cnt >= 50:
            score += 20
        elif cur_cnt >= 20:
            score += 15
        elif cur_cnt >= 5:
            score += 10

        financial_health = {
            "score": int(score),
            "label": (
                "excellent" if score >= 85 else
                "good" if score >= 70 else
                "warning" if score >= 50 else
                "critical"
            ),
        }

        # -------------------------
        # STOCK HEALTH
        # -------------------------
        expiry_limit = today + timedelta(days=30)

        expired_batches = ProductBatch.objects.filter(
            product__pharmacy=pharmacy,
            quantity__gt=0,
            expiry_date__lt=today
        ).count()

        expiring_soon_batches = ProductBatch.objects.filter(
            product__pharmacy=pharmacy,
            quantity__gt=0,
            expiry_date__range=(today, expiry_limit)
        ).count()

        low_stock_count = 0
        products = Product.objects.filter(pharmacy=pharmacy, is_active=True)

        for p in products:
            stock = ProductBatch.objects.filter(
                product=p
            ).aggregate(total=Sum("quantity"))["total"] or 0

            if stock <= (p.min_stock_level or 0):
                low_stock_count += 1

        stock_index = 100
        stock_index -= expired_batches * 2
        stock_index -= expiring_soon_batches * 1
        stock_index -= low_stock_count * 3
        stock_index = max(0, min(100, stock_index))

        stock_health = {
            "index": int(stock_index),
            "label": (
                "healthy" if stock_index >= 75 else
                "warning" if stock_index >= 50 else
                "critical"
            ),
        }

        # -------------------------
        # FORECAST (baseline)
        # -------------------------
        last14_start = today - timedelta(days=13)

        last14_sales = Sale.objects.filter(
            pharmacy=pharmacy,
            created_at__date__gte=last14_start,
            created_at__date__lte=today,
        ).aggregate(revenue=Sum("total_price"))["revenue"] or 0

        avg_daily = float(last14_sales) / 14.0
        forecast_7d = [round(avg_daily, 2)] * 7

        # -------------------------
        # ALERTS
        # -------------------------
        alerts = []

        if anomaly:
            alerts.append({"type": "revenue_anomaly", "severity": "high"})

        if expired_batches > 0:
            alerts.append({"type": "expired_stock", "severity": "high"})

        return Response({
            "period": {"current_start": current_start, "current_end": current_end},
            "financial_health_score": financial_health,
            "stock_health_index": stock_health,
            "underperforming_products": [],
            "sales_forecast_7d": {
                "avg_daily": round(avg_daily, 2),
                "next_7_days": forecast_7d,
            },
            "alert_intelligence": alerts,
        })
