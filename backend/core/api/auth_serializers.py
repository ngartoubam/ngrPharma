from rest_framework import serializers


class PinLoginSerializer(serializers.Serializer):
    pharmacy_id = serializers.UUIDField()
    pin = serializers.CharField(min_length=4, max_length=12)
