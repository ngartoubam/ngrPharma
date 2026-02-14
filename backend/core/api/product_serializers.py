from rest_framework import serializers
from django.db import models
from core.models import Product, ProductBatch



class ProductStockSerializer(serializers.ModelSerializer):
    stock = serializers.IntegerField(read_only=True)
    nearest_expiry = serializers.DateField(read_only=True)
    low_stock = serializers.BooleanField(read_only=True)

    class Meta:
        model = Product
        fields = [
            "id",
            "name",
            "generic_name",
            "dosage",
            "form",
            "stock",
            "min_stock_level",
            "low_stock",
            "nearest_expiry",
        ]


class LowStockProductSerializer(serializers.ModelSerializer):
    stock = serializers.IntegerField()
    low_stock = serializers.BooleanField()
    nearest_expiry = serializers.DateField()

    class Meta:
        model = Product
        fields = [
            "id",
            "name",
            "dosage",
            "stock",
            "min_stock_level",
            "low_stock",
            "nearest_expiry",
        ]


class ExpiringBatchSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source="product.name")
    dosage = serializers.CharField(source="product.dosage")

    class Meta:
        model = ProductBatch
        fields = [
            "id",
            "product_name",
            "dosage",
            "quantity",
            "expiry_date",
        ]
