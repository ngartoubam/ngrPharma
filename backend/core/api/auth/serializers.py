# core/api/auth/serializers.py

from rest_framework import serializers
from core.models import Pharmacy


# =========================================================
# 🔐 PIN LOGIN (MODE PHARMACIE / CAISSE)
# =========================================================
class PinLoginSerializer(serializers.Serializer):
    """
    Login pour pharmacien / gérant via PIN
    """
    pharmacy_id = serializers.UUIDField()
    pin = serializers.CharField(
        min_length=4,
        max_length=12,
        write_only=True
    )

    def validate_pharmacy_id(self, value):
        """
        Vérifie que la pharmacie existe
        """
        if not Pharmacy.objects.filter(id=value).exists():
            raise serializers.ValidationError("Pharmacy not found")
        return value


# =========================================================
# 🔐 SAAS ADMIN LOGIN (EMAIL + PASSWORD)
# =========================================================
class AdminLoginSerializer(serializers.Serializer):
    """
    Login réservé au SaaS Admin (email + password)
    """
    email = serializers.EmailField()
    password = serializers.CharField(
        write_only=True,
        min_length=6,
        trim_whitespace=False
    )

    def validate_email(self, value):
        return value.lower()


# =========================================================
# 🔐 OPTIONAL — PHARMACY EMAIL LOGIN (FUTURE READY)
# =========================================================
class PharmacyEmailLoginSerializer(serializers.Serializer):
    """
    (Optionnel futur)
    Login pharmacie via email + password
    Si un jour tu abandonnes le PIN.
    """
    pharmacy_code = serializers.CharField(max_length=20)
    email = serializers.EmailField()
    password = serializers.CharField(
        write_only=True,
        min_length=6,
        trim_whitespace=False
    )