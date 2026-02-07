from rest_framework import serializers
from django.db import transaction
from core.models import Product, Sale

class SaleCreateSerializer(serializers.Serializer):
    product_id = serializers.UUIDField()
    quantity = serializers.IntegerField(min_value=1)

    def validate(self, data):
        product = Product.objects.get(id=data["product_id"], is_active=True)
        total_stock = sum(b.quantity for b in product.batches.all())

        if data["quantity"] > total_stock:
            raise serializers.ValidationError("Stock insuffisant")

        data["product"] = product
        return data

    def create(self, validated_data):
        product = validated_data["product"]
        qty_to_sell = validated_data["quantity"]

        with transaction.atomic():
            for batch in product.batches.all():  # FIFO
                if qty_to_sell <= 0:
                    break

                take = min(batch.quantity, qty_to_sell)
                batch.quantity -= take
                batch.save()

                qty_to_sell -= take

            sale = Sale.objects.create(
                pharmacy=product.pharmacy,
                product=product,
                quantity=validated_data["quantity"],
                unit_price=product.unit_price,
                total_price=product.unit_price * validated_data["quantity"],
            )

        return sale
