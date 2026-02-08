from rest_framework import serializers
from django.db import transaction, models

from core.models import Product, Sale, ProductBatch


# =========================
# CREATE SALE (FIFO)
# =========================
class SaleCreateSerializer(serializers.Serializer):
    product_id = serializers.UUIDField()
    quantity = serializers.IntegerField(min_value=1)

    def validate(self, data):
        request = self.context["request"]
        pharmacy = request.user.pharmacy

        try:
            product = Product.objects.get(
                id=data["product_id"],
                pharmacy=pharmacy,
                is_active=True
            )
        except Product.DoesNotExist:
            raise serializers.ValidationError(
                "Produit invalide ou non autorisé pour cette pharmacie"
            )

        # 🔎 Stock total réel (tous lots confondus)
        total_stock = ProductBatch.objects.filter(
            product=product,
            quantity__gt=0
        ).aggregate(total=models.Sum("quantity"))["total"] or 0

        if data["quantity"] > total_stock:
            raise serializers.ValidationError("Stock insuffisant")

        data["product"] = product
        return data

    def create(self, validated_data):
        product = validated_data["product"]
        qty_to_sell = validated_data["quantity"]
        pharmacy = product.pharmacy

        with transaction.atomic():
            # 🔁 FIFO strict
            batches = ProductBatch.objects.filter(
                product=product,
                quantity__gt=0
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

        return sale


# =========================
# SALE HISTORY
# =========================
class SaleListSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source="product.name", read_only=True)

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
