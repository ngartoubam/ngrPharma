from datetime import timedelta
from django.db.models import Sum, Min, Q
from django.utils.timezone import now

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions
from rest_framework.permissions import IsAuthenticated

from drf_spectacular.utils import extend_schema

from core.models import (
    Product,
)

from core.permissions import IsAdminOrGerant

from .serializers import (
    ProductStockSerializer,
    LowStockProductSerializer,
    ExpiringBatchSerializer,
)

# ======================================================
# STOCK GLOBAL PAR PRODUIT
# ======================================================
class ProductStockListView(APIView):
    permission_classes = [IsAuthenticated, IsAdminOrGerant]

    @extend_schema(
        summary="Liste du stock global par produit",
        responses=ProductStockSerializer(many=True),
    )
    def get(self, request):
        pharmacy = request.user.pharmacy

        products = (
            Product.objects
            .filter(pharmacy=pharmacy, is_active=True)
            .annotate(
                stock=Sum("batches__quantity", filter=Q(batches__quantity__gt=0)),
                nearest_expiry=Min("batches__expiry_date")
            )
        )

        for product in products:
            product.stock = product.stock or 0
            product.low_stock = product.stock <= product.min_stock_level

        return Response(ProductStockSerializer(products, many=True).data)


# ======================================================
# LOW STOCK PRODUCTS
# ======================================================
class LowStockProductListView(APIView):
    permission_classes = [permissions.IsAuthenticated, IsAdminOrGerant]

    @extend_schema(
        summary="Produits en stock bas",
        description="Liste des produits dont le stock est inférieur ou égal au seuil minimum",
        responses=LowStockProductSerializer(many=True),
    )
    def get(self, request):
        pharmacy = request.user.pharmacy

        products = (
            Product.objects
            .filter(pharmacy=pharmacy, is_active=True)
            .annotate(
                stock=Sum(
                    "batches__quantity",
                    filter=Q(batches__quantity__gt=0)
                )
            )
        )

        low_stock_products = []

        for product in products:
            product.stock = product.stock or 0
            if product.stock <= product.min_stock_level:
                low_stock_products.append(product)

        return Response(LowStockProductSerializer(low_stock_products, many=True).data)


# ======================================================
# PRODUITS EXPIRÉS OU PROCHES EXPIRATION
# ======================================================
class ProductExpiryAlertView(APIView):
    permission_classes = [permissions.IsAuthenticated, IsAdminOrGerant]

    @extend_schema(
        summary="Produits expirés ou proches expiration",
        responses=ProductStockSerializer(many=True),
    )
    def get(self, request):
        pharmacy = request.user.pharmacy
        today = now().date()
        limit_date = today + timedelta(days=30)

        products = (
            Product.objects
            .filter(pharmacy=pharmacy, is_active=True)
            .annotate(
                stock=Sum(
                    "batches__quantity",
                    filter=Q(batches__quantity__gt=0)
                ),
                nearest_expiry=Min(
                    "batches__expiry_date",
                    filter=Q(
                        batches__quantity__gt=0,
                        batches__expiry_date__lte=limit_date
                    )
                ),
            )
            .filter(nearest_expiry__isnull=False)
            .order_by("nearest_expiry")
        )

        for p in products:
            p.stock = p.stock or 0
            p.is_expired = p.nearest_expiry < today
            p.is_expiring_soon = today <= p.nearest_expiry <= limit_date

        return Response(ProductStockSerializer(products, many=True).data)
