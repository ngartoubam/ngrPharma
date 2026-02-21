from rest_framework import serializers


class CheckoutSessionSerializer(serializers.Serializer):
    price_id = serializers.CharField()


class CheckoutSessionResponseSerializer(serializers.Serializer):
    checkout_url = serializers.URLField()


class BillingPortalResponseSerializer(serializers.Serializer):
    portal_url = serializers.URLField()