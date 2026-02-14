from datetime import timedelta
from django.db.models import Sum, Min, Q
from django.utils.timezone import now

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions

from drf_spectacular.utils import extend_schema

from core.models import Product, ProductBatch
from core.permissions import IsAdminOrGerant

from core.api.product_serializers import (
    ProductStockSerializer,
    LowStockProductSerializer,
    ExpiringBatchSerializer,
)

# ======================================================
# STOCK GLOBAL PAR PRODUIT
# ======================================================
class ProductStockListView(APIView):
    permission_classes = [permissions.IsAuthenticated, IsAdminOrGerant,]

    @extend_schema(
        responses={200: ProductStockSerializer(many=True)},
        summary="Stock réel par produit",
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
                ),
                nearest_expiry=Min(
                    "batches__expiry_date",
                    filter=Q(batches__quantity__gt=0)
                ),
            )
        )

        for product in products:
            product.stock = product.stock or 0
            product.low_stock = product.stock <= product.min_stock_level

        return Response(ProductStockSerializer(products, many=True).data)


# ======================================================
# PRODUITS EN STOCK BAS
# ======================================================
class LowStockProductListView(APIView):
    permission_classes = [permissions.IsAuthenticated, IsAdminOrGerant]

    @extend_schema(
        responses={200: LowStockProductSerializer(many=True)},
        summary="Produits en stock bas",
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

        low_stock = []
        for p in products:
            p.stock = p.stock or 0
            if p.stock <= p.min_stock_level:
                low_stock.append(p)

        return Response(LowStockProductSerializer(low_stock, many=True).data)


# ======================================================
# ALERTES PRODUITS (EXPIRES / PROCHES EXPIRATION)
# ======================================================
class ProductExpiryAlertView(APIView):
    permission_classes = [permissions.IsAuthenticated, IsAdminOrGerant]

    @extend_schema(
        responses={200: ProductStockSerializer(many=True)},
        summary="Alertes produits expirés ou proches d’expiration",
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


# ======================================================
# LOTS EXPIRES / PROCHES EXPIRATION (DETAIL)
# ======================================================
class ExpiringSoonProductListView(APIView):
    permission_classes = [permissions.IsAuthenticated, IsAdminOrGerant]

    @extend_schema(
        responses={200: ExpiringBatchSerializer(many=True)},
        summary="Lots expirés ou proches d’expiration",
    )
    def get(self, request):
        pharmacy = request.user.pharmacy
        today = now().date()
        limit_date = today + timedelta(days=30)

        batches = (
            ProductBatch.objects
            .filter(
                product__pharmacy=pharmacy,
                quantity__gt=0,
                expiry_date__lte=limit_date
            )
            .select_related("product")
            .order_by("expiry_date")
        )

        return Response(ExpiringBatchSerializer(batches, many=True).data)


# ======================================================
# Expired Batch ListView
# ======================================================

class ExpiredBatchListView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(
        responses={200: ExpiringBatchSerializer(many=True)},
        summary="Lots expirés",
        description="Lots expirés encore en stock (vente bloquée)",
    )
    def get(self, request):
        pharmacy = request.user.pharmacy
        today = date.today()

        batches = (
            ProductBatch.objects
            .filter(
                product__pharmacy=pharmacy,
                quantity__gt=0,
                expiry_date__lt=today
            )
            .select_related("product")
            .order_by("expiry_date")
        )

        serializer = ExpiringBatchSerializer(batches, many=True)
        return Response(serializer.data)


# ======================================================
# Expiring Soon Batch ListView
# ======================================================

class ExpiringSoonBatchListView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(
        responses={200: ExpiringBatchSerializer(many=True)},
        summary="Lots proches d’expiration",
        description="Lots expirant dans les 30 prochains jours",
    )
    def get(self, request):
        pharmacy = request.user.pharmacy
        today = date.today()
        limit = today + timedelta(days=30)

        batches = (
            ProductBatch.objects
            .filter(
                product__pharmacy=pharmacy,
                quantity__gt=0,
                expiry_date__range=(today, limit)
            )
            .select_related("product")
            .order_by("expiry_date")
        )

        serializer = ExpiringBatchSerializer(batches, many=True)
        return Response(serializer.data)
