from rest_framework import serializers


# =====================================================
# FINANCE DASHBOARD RESPONSE
# =====================================================

class FinanceDashboardResponseSerializer(serializers.Serializer):
    period = serializers.DictField()
    current = serializers.DictField()
    previous = serializers.DictField()
    evolution_percent = serializers.DictField()
    trend = serializers.DictField()
    anomaly = serializers.DictField()
    chart = serializers.DictField()
    stock_value = serializers.FloatField()


# =====================================================
# MONTHLY FINANCE
# =====================================================

class MonthlyFinanceSerializer(serializers.Serializer):
    month = serializers.DateTimeField()
    revenue = serializers.FloatField()
    cogs = serializers.FloatField()
    gross_margin = serializers.FloatField()
    average_ticket = serializers.FloatField()


# =====================================================
# STOCK ROTATION
# =====================================================

class StockRotationSerializer(serializers.Serializer):
    product = serializers.CharField()
    sold_quantity = serializers.FloatField()
    current_stock = serializers.FloatField()
    rotation_ratio = serializers.FloatField()


# =====================================================
# TOP PRODUCTS
# =====================================================

class TopProductSerializer(serializers.Serializer):
    product = serializers.CharField()
    quantity_sold = serializers.FloatField()
    revenue = serializers.FloatField()
    gross_margin = serializers.FloatField()