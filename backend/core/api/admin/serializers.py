from rest_framework import serializers
from core.models import Pharmacy


class AdminPharmacySerializer(serializers.ModelSerializer):
    """
    Serializer CRUD Pharmacie (SaaS Admin)
    """

    class Meta:
        model = Pharmacy
        fields = [
            "id",
            "code",
            "name",
            "type",
            "city",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]

    # ============================================
    # VALIDATION CODE UNIQUE + NORMALISATION
    # ============================================
    def validate_code(self, value):
        value = value.upper().strip()

        qs = Pharmacy.objects.filter(code=value)

        # Exclure instance actuelle en cas d'update
        if self.instance:
            qs = qs.exclude(pk=self.instance.pk)

        if qs.exists():
            raise serializers.ValidationError("Pharmacy code already exists.")

        return value

    # ============================================
    # CREATE OVERRIDE (future extensible)
    # ============================================
    def create(self, validated_data):
        validated_data["code"] = validated_data["code"].upper().strip()
        return super().create(validated_data)

    # ============================================
    # UPDATE OVERRIDE (future extensible)
    # ============================================
    def update(self, instance, validated_data):
        if "code" in validated_data:
            validated_data["code"] = validated_data["code"].upper().strip()

        return super().update(instance, validated_data)
