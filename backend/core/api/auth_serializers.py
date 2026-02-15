# backend/core/api/auth_serializers.py

from rest_framework import serializers


# ============================================
# PIN LOGIN (MODE CAISSE)
# ============================================
class PinLoginSerializer(serializers.Serializer):
    pharmacy_id = serializers.UUIDField()
    pin = serializers.CharField(min_length=4, max_length=12)


# ============================================
# EMAIL / PASSWORD LOGIN (SaaS)
# ============================================
class EmailLoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, min_length=4)
