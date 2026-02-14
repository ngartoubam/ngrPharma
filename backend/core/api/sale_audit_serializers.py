from rest_framework import serializers
from core.models import SaleAuditLog


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
