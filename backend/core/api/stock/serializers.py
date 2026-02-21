from rest_framework import serializers
from core.models import StockEntry, StockEntryItem


# =====================================================
# CREATE STOCK ENTRY (Draft)
# =====================================================
class StockEntryCreateSerializer(serializers.ModelSerializer):

    class Meta:
        model = StockEntry
        fields = [
            "id",
            "supplier",
            "invoice_number",
            "total_amount",
        ]
        read_only_fields = ["id"]

    def create(self, validated_data):
        request = self.context["request"]

        return StockEntry.objects.create(
            pharmacy=request.user.pharmacy,
            status="draft",
            **validated_data
        )


# =====================================================
# LIST STOCK ENTRIES
# =====================================================
class StockEntryListSerializer(serializers.ModelSerializer):

    class Meta:
        model = StockEntry
        fields = [
            "id",
            "supplier",
            "invoice_number",
            "total_amount",
            "status",
            "created_at",
        ]


# =====================================================
# DETAIL STOCK ENTRY
# =====================================================
class StockEntryDetailSerializer(serializers.ModelSerializer):

    class Meta:
        model = StockEntry
        fields = [
            "id",
            "supplier",
            "invoice_number",
            "total_amount",
            "status",
            "created_at",
        ]


# =====================================================
# VALIDATION SERIALIZER
# =====================================================
class StockEntryValidationSerializer(serializers.ModelSerializer):

    class Meta:
        model = StockEntry
        fields = ["status"]

    def update(self, instance, validated_data):
        instance.status = "validated"
        instance.save(update_fields=["status"])
        return instance