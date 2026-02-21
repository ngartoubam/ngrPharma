from rest_framework import serializers
from core.models import Pharmacy


class AdminPharmacySerializer(serializers.ModelSerializer):
    """
    Serializer CRUD Pharmacie (SaaS Admin - Premium Version)
    """

    # ================================
    # READ-ONLY SaaS Fields
    # ================================
    stripe_customer_id = serializers.CharField(read_only=True)
    stripe_subscription_id = serializers.CharField(read_only=True)
    subscription_status = serializers.CharField(read_only=True)
    current_period_end = serializers.DateTimeField(read_only=True)

    class Meta:
        model = Pharmacy
        fields = [
            # Core
            "id",
            "code",
            "name",
            "type",
            "country",
            "city",

            # SaaS / Activation
            "is_active",
            "suspended_reason",

            # SaaS / Billing (readonly)
            "plan",
            "subscription_status",
            "stripe_customer_id",
            "stripe_subscription_id",
            "current_period_end",

            # Metadata
            "created_at",
        ]
        read_only_fields = [
            "id",
            "created_at",
            "stripe_customer_id",
            "stripe_subscription_id",
            "subscription_status",
            "current_period_end",
        ]

    def validate_code(self, value):
        if not value:
            return value
        value = value.upper().strip()

        qs = Pharmacy.objects.filter(code=value)
        if self.instance:
            qs = qs.exclude(pk=self.instance.pk)

        if qs.exists():
            raise serializers.ValidationError("Pharmacy code already exists.")
        return value

    def validate_country(self, value):
        # optionnel : normalisation simple
        if value is None:
            return value
        return value.strip() or None

    def create(self, validated_data):
        if validated_data.get("code"):
            validated_data["code"] = validated_data["code"].upper().strip()

        # Par défaut nouvelle pharmacie = inactive subscription
        validated_data.setdefault("subscription_status", "inactive")
        return super().create(validated_data)

    def update(self, instance, validated_data):
        if validated_data.get("code"):
            validated_data["code"] = validated_data["code"].upper().strip()
        if "country" in validated_data:
            validated_data["country"] = (validated_data["country"] or "").strip() or None
        return super().update(instance, validated_data)