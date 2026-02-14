from rest_framework import serializers
from django.db import transaction, models
from django.utils.timezone import now

from core.models import (
    Product,
    Sale,
    ProductBatch,
    SaleAuditLog,
)

from core.services.notifications import (
    notify_blocked_sale,
    notify_expired_products,
    notify_expiring_soon_products,
    notify_low_stock,
)


# =========================
# CREATE SALE (FIFO sécurisé + audit + notifications)
# =========================
class SaleCreateSerializer(serializers.Serializer):
    product_id = serializers.UUIDField()
    quantity = serializers.IntegerField(min_value=1)

    # ---------------------------------
    # Audit + notification vente bloquée
    # ---------------------------------
    def _log_blocked_sale(self, *, request, product, quantity, reason, message):
        audit_log = SaleAuditLog.objects.create(
            pharmacy=request.user.pharmacy,
            user=request.user,
            product=product,
            requested_quantity=quantity,
            reason=reason,
            message=message,
        )

        # 🔔 Notification admin
        notify_blocked_sale(audit_log)

    # ---------------------------------
    # VALIDATION
    # ---------------------------------
    def validate(self, data):
        request = self.context["request"]
        pharmacy = request.user.pharmacy
        today = now().date()
        quantity = data["quantity"]

        # 🔎 Produit autorisé pour la pharmacie
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
                message="Produit inexistant ou non autorisé pour cette pharmacie",
            )
            raise serializers.ValidationError(
                "Produit invalide ou non autorisé pour cette pharmacie"
            )

        # 🔕 Produit inactif
        if not product.is_active:
            self._log_blocked_sale(
                request=request,
                product=product,
                quantity=quantity,
                reason="inactive_product",
                message="Produit inactif",
            )
            raise serializers.ValidationError("Produit inactif")

        # 🔒 Stock VALIDE = lots NON expirés uniquement
        valid_stock = ProductBatch.objects.filter(
            product=product,
            quantity__gt=0,
            expiry_date__gte=today
        ).aggregate(
            total=models.Sum("quantity")
        )["total"] or 0

        # ⛔ Tous les lots expirés
        if valid_stock == 0:
            self._log_blocked_sale(
                request=request,
                product=product,
                quantity=quantity,
                reason="expired_stock",
                message="Tous les lots disponibles sont expirés",
            )
            raise serializers.ValidationError(
                "Vente bloquée : tous les lots sont expirés"
            )

        # ⛔ Stock insuffisant
        if quantity > valid_stock:
            self._log_blocked_sale(
                request=request,
                product=product,
                quantity=quantity,
                reason="insufficient_stock",
                message=f"Stock valide: {valid_stock}, quantité demandée: {quantity}",
            )
            raise serializers.ValidationError(
                "Stock insuffisant (lots expirés exclus)"
            )

        data["product"] = product
        return data

    # ---------------------------------
    # CREATE (FIFO strict)
    # ---------------------------------
    def create(self, validated_data):
        request = self.context["request"]
        product = validated_data["product"]
        qty_to_sell = validated_data["quantity"]
        pharmacy = product.pharmacy
        today = now().date()

        with transaction.atomic():
            # 🔁 FIFO STRICT + NON EXPIRÉ
            batches = ProductBatch.objects.filter(
                product=product,
                quantity__gt=0,
                expiry_date__gte=today
            ).order_by("expiry_date", "created_at")

            remaining = qty_to_sell

            for batch in batches:
                if remaining == 0:
                    break

                take = min(batch.quantity, remaining)
                batch.quantity -= take
                batch.save(update_fields=["quantity"])
                remaining -= take

            sale = Sale.objects.create(
                pharmacy=pharmacy,
                product=product,
                quantity=qty_to_sell,
                unit_price=product.unit_price,
                total_price=product.unit_price * qty_to_sell,
            )

        # 🔔 Notifications post-vente (dashboard / email)
        notify_expired_products(pharmacy)
        notify_expiring_soon_products(pharmacy)
        notify_low_stock(pharmacy)

        return sale


# =========================
# SALE HISTORY
# =========================
class SaleListSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(
        source="product.name",
        read_only=True
    )

    class Meta:
        model = Sale
        fields = [
            "id",
            "product_name",
            "quantity",
            "unit_price",
            "total_price",
            "created_at",
        ]


# =========================
# SALE AUDIT LIST
# =========================
class SaleAuditLogSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(
        source="product.name",
        read_only=True
    )
    user_name = serializers.CharField(
        source="user.name",
        read_only=True
    )

    class Meta:
        model = SaleAuditLog
        fields = [
            "id",
            "product_name",
            "user_name",
            "requested_quantity",
            "reason",
            "message",
            "created_at",
        ]
