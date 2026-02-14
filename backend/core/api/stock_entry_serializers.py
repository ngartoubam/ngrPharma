from rest_framework import serializers
from django.db import transaction
from django.utils.timezone import now


from core.models import (
    StockEntry,
    StockEntryItem,
    Product,
    ProductBatch,
    SaleAuditLog,
)


# ================================================
# STOCK ENTRY ITEM SERIALIZER
# ================================================
class StockEntryItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(
        source="product.name",
        read_only=True
    )

    class Meta:
        model = StockEntryItem
        fields = [
            "id",
            "product",
            "product_name",
            "quantity",
            "purchase_price",
            "expiry_date",
            "line_total",
        ]
        read_only_fields = ["line_total"]


# ================================================
# CREATE STOCK ENTRY
# ================================================
class StockEntryCreateSerializer(serializers.ModelSerializer):
    items = StockEntryItemSerializer(many=True)

    class Meta:
        model = StockEntry
        fields = [
            "id",
            "supplier",
            "invoice_number",
            "status",
            "items",
        ]

    def create(self, validated_data):
        request = self.context["request"]
        pharmacy = request.user.pharmacy
        items_data = validated_data.pop("items")

        with transaction.atomic():

            entry = StockEntry.objects.create(
                pharmacy=pharmacy,
                status="validated",
                **validated_data
            )

            total_amount = 0

            for item_data in items_data:
                product = item_data["product"]
                quantity = item_data["quantity"]
                purchase_price = item_data["purchase_price"]
                expiry_date = item_data["expiry_date"]

                line_total = quantity * purchase_price
                total_amount += line_total

                # 🔹 Création ligne
                StockEntryItem.objects.create(
                    stock_entry=entry,
                    product=product,
                    quantity=quantity,
                    purchase_price=purchase_price,
                    expiry_date=expiry_date,
                    line_total=line_total,
                )

                # 🔹 Création lot automatique
                ProductBatch.objects.create(
                    product=product,
                    quantity=quantity,
                    expiry_date=expiry_date,
                )

            entry.total_amount = total_amount
            entry.save(update_fields=["total_amount"])

            # 🔹 Audit automatique
            SaleAuditLog.objects.create(
                pharmacy=pharmacy,
                user=request.user,
                product=None,
                action="SUCCESS",
                reason="other",
                requested_quantity=0,
                message=f"Entrée de stock validée (ID: {entry.id})",
            )

        return entry


# ================================================
# LIST SERIALIZER
# ================================================
class StockEntryListSerializer(serializers.ModelSerializer):
    supplier_name = serializers.CharField(
        source="supplier.name",
        read_only=True
    )

    class Meta:
        model = StockEntry
        fields = [
            "id",
            "supplier_name",
            "invoice_number",
            "total_amount",
            "status",
            "created_at",
        ]


# ================================================
# DETAIL SERIALIZER
# ================================================
class StockEntryDetailSerializer(serializers.ModelSerializer):
    supplier_name = serializers.CharField(
        source="supplier.name",
        read_only=True
    )

    items = StockEntryItemSerializer(many=True)

    class Meta:
        model = StockEntry
        fields = [
            "id",
            "supplier_name",
            "invoice_number",
            "total_amount",
            "status",
            "created_at",
            "items",
        ]





class StockEntryValidationSerializer(serializers.Serializer):
    """
    Validation d’un bon d’entrée (workflow pro)
    """

    def validate(self, data):
        entry = self.context["entry"]

        if entry.status == "validated":
            raise serializers.ValidationError("Ce bon est déjà validé.")

        return data

    def save(self):
        entry = self.context["entry"]

        # 🔹 Création des lots réels
        for item in entry.items.all():
            ProductBatch.objects.create(
                product=item.product,
                quantity=item.quantity,
                expiry_date=item.expiry_date
            )

        entry.status = "validated"
        entry.save(update_fields=["status"])

        return entry
