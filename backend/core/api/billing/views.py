# backend/core/api/billing/views.py

import stripe
from django.conf import settings
from django.utils import timezone

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions, serializers

from core.models import Pharmacy
from core.permissions import IsSubscriptionActive

stripe.api_key = settings.STRIPE_SECRET_KEY


# ======================================================
# SERIALIZERS (Swagger Clean)
# ======================================================

class CheckoutRequestSerializer(serializers.Serializer):
    price_id = serializers.CharField()


class CheckoutResponseSerializer(serializers.Serializer):
    url = serializers.URLField()


class SubscriptionInfoSerializer(serializers.Serializer):
    plan = serializers.CharField()
    subscription_status = serializers.CharField()
    current_period_end = serializers.DateTimeField(allow_null=True)


# ======================================================
# CREATE STRIPE CHECKOUT SESSION
# ======================================================

class CreateCheckoutSessionView(APIView):

    permission_classes = [permissions.IsAuthenticated]
    serializer_class = CheckoutRequestSerializer

    def post(self, request):

        user = request.user

        if getattr(user, "is_saas_admin", False):
            return Response(
                {"error": "SaaS Admin cannot subscribe."},
                status=status.HTTP_400_BAD_REQUEST
            )

        pharmacy = getattr(user, "pharmacy", None)

        if not pharmacy:
            return Response(
                {"error": "User not linked to pharmacy."},
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer = CheckoutRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        price_id = serializer.validated_data["price_id"]

        try:

            # Create Stripe customer if not exists
            if not pharmacy.stripe_customer_id:
                customer = stripe.Customer.create(
                    name=pharmacy.name,
                    metadata={
                        "pharmacy_id": str(pharmacy.id),
                        "country": getattr(pharmacy, "country", "")
                    }
                )
                pharmacy.stripe_customer_id = customer.id
                pharmacy.save()

            session = stripe.checkout.Session.create(
                mode="subscription",
                customer=pharmacy.stripe_customer_id,
                payment_method_types=["card"],
                line_items=[{"price": price_id, "quantity": 1}],
                success_url=settings.STRIPE_SUCCESS_URL,
                cancel_url=settings.STRIPE_CANCEL_URL,
            )

            return Response(
                {"url": session.url},
                status=status.HTTP_200_OK
            )

        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )


# ======================================================
# STRIPE BILLING PORTAL
# ======================================================

class CreateBillingPortalView(APIView):

    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):

        user = request.user

        if getattr(user, "is_saas_admin", False):
            return Response(
                {"error": "SaaS Admin has no billing portal."},
                status=status.HTTP_400_BAD_REQUEST
            )

        pharmacy = getattr(user, "pharmacy", None)

        if not pharmacy or not pharmacy.stripe_customer_id:
            return Response(
                {"error": "No Stripe customer found."},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            portal_session = stripe.billing_portal.Session.create(
                customer=pharmacy.stripe_customer_id,
                return_url=settings.STRIPE_SUCCESS_URL,
            )

            return Response(
                {"url": portal_session.url},
                status=status.HTTP_200_OK
            )

        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )


# ======================================================
# GET CURRENT SUBSCRIPTION INFO
# ======================================================

class MeSubscriptionView(APIView):

    permission_classes = [permissions.IsAuthenticated]
    serializer_class = SubscriptionInfoSerializer

    def get(self, request):

        user = request.user

        if getattr(user, "is_saas_admin", False):
            return Response(
                {
                    "plan": "enterprise",
                    "subscription_status": "active",
                    "current_period_end": None,
                }
            )

        pharmacy = getattr(user, "pharmacy", None)

        if not pharmacy:
            return Response(
                {"error": "User not linked to pharmacy."},
                status=status.HTTP_400_BAD_REQUEST
            )

        return Response({
            "plan": pharmacy.plan,
            "subscription_status": pharmacy.subscription_status,
            "current_period_end": pharmacy.current_period_end,
        })