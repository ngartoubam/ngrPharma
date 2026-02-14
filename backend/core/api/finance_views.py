from datetime import date, timedelta
from django.db.models import Sum, F, ExpressionWrapper, DecimalField, Count
from django.db.models.functions import TruncMonth
from django.utils.timezone import now

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions
from rest_framework import serializers
from drf_spectacular.utils import extend_schema

from core.models import Sale, ProductBatch, Product
from core.permissions import IsAdminOrGerant


# =====================================================
# SERIALIZERS (FOR SWAGGER DOCUMENTATION)
# =====================================================

class FinanceCurrentSerializer(serializers.Serializer):
    revenue = serializers.FloatField()
    cogs = serializers.FloatField()
    gross_margin = serializers.FloatField()
    sales_count = serializers.IntegerField()
    average_ticket = serializers.FloatField()


class FinancePreviousSerializer(serializers.Serializer):
    revenue = serializers.FloatField()
    cogs = serializers.FloatField()
    gross_margin = serializers.FloatField()


class FinanceEvolutionSerializer(serializers.Serializer):
    revenue = serializers.FloatField()
    gross_margin = serializers.FloatField()


class FinanceTrendSerializer(serializers.Serializer):
    revenue = serializers.CharField()
    gross_margin = serializers.CharField()


class FinanceAnomalySerializer(serializers.Serializer):
    is_anomaly = serializers.BooleanField()
    revenue_drop_percent = serializers.FloatField()
    message = serializers.CharField(allow_null=True)


class FinanceChartSerializer(serializers.Serializer):
    labels = serializers.ListField(child=serializers.CharField())
    revenue_series = serializers.ListField(child=serializers.FloatField())
    margin_series = serializers.ListField(child=serializers.FloatField())


class FinanceDashboardResponseSerializer(serializers.Serializer):
    period = serializers.DictField()
    current = FinanceCurrentSerializer()
    previous = FinancePreviousSerializer()
    evolution_percent = FinanceEvolutionSerializer()
    trend = FinanceTrendSerializer()
    anomaly = FinanceAnomalySerializer()
    chart = FinanceChartSerializer()
    stock_value = serializers.FloatField()


class MonthlyFinanceSerializer(serializers.Serializer):
    month = serializers.DateTimeField()
    revenue = serializers.FloatField()
    cogs = serializers.FloatField()
    gross_margin = serializers.FloatField()
    average_ticket = serializers.FloatField()


class StockRotationSerializer(serializers.Serializer):
    product = serializers.CharField()
    sold_quantity = serializers.FloatField()
    current_stock = serializers.FloatField()
    rotation_ratio = serializers.FloatField()


# =====================================================
# FINANCIAL DASHBOARD
# =====================================================
class FinanceDashboardView(APIView):

    permission_classes = [permissions.IsAuthenticated, IsAdminOrGerant]

    @extend_schema(
        summary="Financial dashboard PRO + analytics + anomaly",
        responses=FinanceDashboardResponseSerializer
    )
    def get(self, request):

        pharmacy = request.user.pharmacy
        today = now().date()

        period = request.query_params.get("period")
        start_param = request.query_params.get("start")
        end_param = request.query_params.get("end")

        if start_param and end_param:
            start = date.fromisoformat(start_param)
            end = date.fromisoformat(end_param)
        else:
            if period == "today":
                start = today
                end = today
            elif period == "last_7_days":
                start = today - timedelta(days=6)
                end = today
            elif period == "this_month":
                start = today.replace(day=1)
                end = today
            else:
                start = today - timedelta(days=29)
                end = today

        end_exclusive = end + timedelta(days=1)

        current_sales = Sale.objects.filter(
            pharmacy=pharmacy,
            created_at__date__gte=start,
            created_at__date__lt=end_exclusive
        )

        current_agg = current_sales.aggregate(
            revenue=Sum("total_price"),
            cogs=Sum("cost_total"),
            sales_count=Count("id")
        )

        current_revenue = current_agg["revenue"] or 0
        current_cogs = current_agg["cogs"] or 0
        current_sales_count = current_agg["sales_count"] or 0
        current_gross_margin = current_revenue - current_cogs
        current_avg_ticket = (
            current_revenue / current_sales_count
            if current_sales_count else 0
        )

        duration = (end - start).days + 1
        prev_end = start - timedelta(days=1)
        prev_start = prev_end - timedelta(days=duration - 1)
        prev_end_exclusive = prev_end + timedelta(days=1)

        previous_sales = Sale.objects.filter(
            pharmacy=pharmacy,
            created_at__date__gte=prev_start,
            created_at__date__lt=prev_end_exclusive
        )

        prev_agg = previous_sales.aggregate(
            revenue=Sum("total_price"),
            cogs=Sum("cost_total")
        )

        prev_revenue = prev_agg["revenue"] or 0
        prev_cogs = prev_agg["cogs"] or 0
        prev_gross_margin = prev_revenue - prev_cogs

        def percent_change(current, previous):
            if previous == 0:
                return 100 if current > 0 else 0
            return ((current - previous) / previous) * 100

        revenue_evolution = percent_change(current_revenue, prev_revenue)
        margin_evolution = percent_change(current_gross_margin, prev_gross_margin)

        def trend_label(value):
            if value > 5:
                return "strong_up"
            elif value > 0:
                return "up"
            elif value < -5:
                return "strong_down"
            elif value < 0:
                return "down"
            return "stable"

        anomaly = {
            "is_anomaly": revenue_evolution < -30,
            "revenue_drop_percent": round(abs(revenue_evolution), 2) if revenue_evolution < 0 else 0,
            "message": "Revenue dropped significantly compared to previous period"
            if revenue_evolution < -30 else None
        }

        chart_data = (
            current_sales
            .annotate(month=TruncMonth("created_at"))
            .values("month")
            .annotate(
                revenue=Sum("total_price"),
                cogs=Sum("cost_total")
            )
            .order_by("month")
        )

        labels = []
        revenue_series = []
        margin_series = []

        for item in chart_data:
            labels.append(str(item["month"].date()))
            rev = item["revenue"] or 0
            cg = item["cogs"] or 0
            revenue_series.append(rev)
            margin_series.append(rev - cg)

        stock_value = ProductBatch.objects.filter(
            product__pharmacy=pharmacy,
            quantity__gt=0
        ).aggregate(
            total=Sum(
                ExpressionWrapper(
                    F("quantity") * F("purchase_price"),
                    output_field=DecimalField(max_digits=12, decimal_places=2)
                )
            )
        )["total"] or 0

        return Response({
            "period": {"start": start, "end": end},
            "current": {
                "revenue": current_revenue,
                "cogs": current_cogs,
                "gross_margin": current_gross_margin,
                "sales_count": current_sales_count,
                "average_ticket": round(current_avg_ticket, 2),
            },
            "previous": {
                "revenue": prev_revenue,
                "cogs": prev_cogs,
                "gross_margin": prev_gross_margin,
            },
            "evolution_percent": {
                "revenue": round(revenue_evolution, 2),
                "gross_margin": round(margin_evolution, 2),
            },
            "trend": {
                "revenue": trend_label(revenue_evolution),
                "gross_margin": trend_label(margin_evolution),
            },
            "anomaly": anomaly,
            "chart": {
                "labels": labels,
                "revenue_series": revenue_series,
                "margin_series": margin_series,
            },
            "stock_value": stock_value,
        })


# =====================================================
# MONTHLY FINANCE
# =====================================================
class MonthlyFinanceView(APIView):

    permission_classes = [permissions.IsAuthenticated, IsAdminOrGerant]

    @extend_schema(responses=MonthlyFinanceSerializer(many=True))
    def get(self, request):

        pharmacy = request.user.pharmacy

        data = (
            Sale.objects
            .filter(pharmacy=pharmacy)
            .annotate(month=TruncMonth("created_at"))
            .values("month")
            .annotate(
                revenue=Sum("total_price"),
                cogs=Sum("cost_total"),
                sales_count=Count("id")
            )
            .order_by("month")
        )

        results = []

        for item in data:
            revenue = item["revenue"] or 0
            cogs = item["cogs"] or 0
            sales_count = item["sales_count"] or 0

            results.append({
                "month": item["month"],
                "revenue": revenue,
                "cogs": cogs,
                "gross_margin": revenue - cogs,
                "average_ticket": (revenue / sales_count) if sales_count else 0
            })

        return Response(results)


# =====================================================
# STOCK ROTATION
# =====================================================
class StockRotationView(APIView):

    permission_classes = [permissions.IsAuthenticated, IsAdminOrGerant]

    @extend_schema(responses=StockRotationSerializer(many=True))
    def get(self, request):

        pharmacy = request.user.pharmacy
        products = Product.objects.filter(pharmacy=pharmacy)

        results = []

        for product in products:

            sold_qty = Sale.objects.filter(
                pharmacy=pharmacy,
                product=product
            ).aggregate(total=Sum("quantity"))["total"] or 0

            current_stock = ProductBatch.objects.filter(
                product=product,
                quantity__gt=0
            ).aggregate(total=Sum("quantity"))["total"] or 0

            rotation_ratio = sold_qty / current_stock if current_stock else 0

            results.append({
                "product": product.name,
                "sold_quantity": sold_qty,
                "current_stock": current_stock,
                "rotation_ratio": round(rotation_ratio, 2),
            })

        return Response(results)
