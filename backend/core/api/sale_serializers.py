from rest_framework import serializers
from django.db import transaction, models
from django.utils.timezone import now
from drf_spectacular.utils import extend_schema_field

from core.models import (
    Product,
    Sale,
    ProductBatch,
    SaleAuditLog,
    SaleBatchConsumption,
)

from core.services.notifications import (
    notify_blocked_sale,
    notify_expired_products,
    notify_expiring_soon_products,
    notify_low_stock,
)


# =====================================================
# CREATE SALE (FIFO strict + COGS réel + audit)
# =====================================================
class SaleCreateSerializer(serializers.Serializer):
    product_id = serializers.UUIDField()
    quantity = serializers.IntegerField(min_value=1)

    # ---------------------------------
    # Audit vente bloquée
    # ---------------------------------
    def _log_blocked_sale(self, *, request, product, quantity, reason, message):
        audit_log = SaleAuditLog.objects.create(
            pharmacy=request.user.pharmacy,
            user=request.user,
            product=product,
            action="BLOCKED",
            requested_quantity=quantity,
            reason=reason,
            message=message,
        )

        notify_blocked_sale(audit_log)

    # ---------------------------------
    # VALIDATION
    # ---------------------------------
    def validate(self, data):
        request = self.context["request"]
        pharmacy = request.user.pharmacy
        today = now().date()
        quantity = data["quantity"]

        try:
            product = Product.objects.get(
                id=data["product_id"],
                pharmacy=pharmacy,
            )
        except Product.DoesNotExist:
            self._log_blocked_sale(
                request=request,
                product=None,
                quantity=quantity,
                reason="unauthorized_product",
                message="Produit inexistant ou non autorisé",
            )
            raise serializers.ValidationError("Produit invalide")

        if not product.is_active:
            self._log_blocked_sale(
                request=request,
                product=product,
                quantity=quantity,
                reason="inactive_product",
                message="Produit inactif",
            )
            raise serializers.ValidationError("Produit inactif")

        valid_stock = ProductBatch.objects.filter(
            product=product,
            quantity__gt=0,
            expiry_date__gte=today
        ).aggregate(total=models.Sum("quantity"))["total"] or 0

        if valid_stock == 0:
            self._log_blocked_sale(
                request=request,
                product=product,
                quantity=quantity,
                reason="expired_stock",
                message="Tous les lots expirés",
            )
            raise serializers.ValidationError("Tous les lots sont expirés")

        if quantity > valid_stock:
            self._log_blocked_sale(
                request=request,
                product=product,
                quantity=quantity,
                reason="insufficient_stock",
                message=f"Stock valide: {valid_stock}",
            )
            raise serializers.ValidationError("Stock insuffisant")

        data["product"] = product
        return data

    # ---------------------------------
    # CREATE (FIFO réel + COGS)
    # ---------------------------------
    def create(self, validated_data):
        request = self.context["request"]
        product = validated_data["product"]
        qty_to_sell = validated_data["quantity"]
        pharmacy = product.pharmacy
        today = now().date()

        with transaction.atomic():

            batches = ProductBatch.objects.filter(
                product=product,
                quantity__gt=0,
                expiry_date__gte=today
            ).order_by("expiry_date", "created_at")

            remaining = qty_to_sell
            total_cost = 0

            sale = Sale.objects.create(
                pharmacy=pharmacy,
                product=product,
                quantity=qty_to_sell,
                unit_price=product.unit_price,
                total_price=product.unit_price * qty_to_sell,
                cost_total=0,
            )

            for batch in batches:
                if remaining == 0:
                    break

                take = min(batch.quantity, remaining)

                batch.quantity -= take
                batch.save(update_fields=["quantity"])

                cost_line = take * batch.purchase_price
                total_cost += cost_line

                SaleBatchConsumption.objects.create(
                    sale=sale,
                    batch=batch,
                    quantity=take,
                    unit_cost=batch.purchase_price,
                    total_cost=cost_line,
                )

                remaining -= take

            sale.cost_total = total_cost
            sale.save(update_fields=["cost_total"])

            SaleAuditLog.objects.create(
                pharmacy=pharmacy,
                user=request.user,
                product=product,
                action="SUCCESS",
                requested_quantity=qty_to_sell,
                reason="other",
                message="Vente effectuée avec succès",
            )

        notify_low_stock(pharmacy)
        notify_expired_products(pharmacy)
        notify_expiring_soon_products(pharmacy)

        return sale


# =====================================================
# SALE HISTORY
# =====================================================
class SaleListSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source="product.name", read_only=True)
    margin = serializers.SerializerMethodField()

    class Meta:
        model = Sale
        fields = [
            "id",
            "product_name",
            "quantity",
            "unit_price",
            "total_price",
            "cost_total",
            "margin",
            "created_at",
        ]

    @extend_schema_field(serializers.FloatField())
    def get_margin(self, obj) -> float:
        return float(obj.total_price - obj.cost_total)


# =====================================================
# SALE AUDIT LIST
# =====================================================
class SaleAuditLogSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source="product.name", read_only=True)
    user_name = serializers.CharField(source="user.name", read_only=True)

    class Meta:
        model = SaleAuditLog
        fields = [
            "id",
            "product_name",
            "user_name",
            "action",
            "requested_quantity",
            "reason",
            "message",
            "created_at",
        ]
