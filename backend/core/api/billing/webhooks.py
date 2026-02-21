# backend/core/api/billing/webhooks.py

import stripe
from django.conf import settings
from django.http import HttpResponse
from django.utils import timezone
from datetime import datetime

from core.models import Pharmacy

stripe.api_key = settings.STRIPE_SECRET_KEY


# ======================================================
# STRIPE WEBHOOK
# ======================================================

def stripe_webhook(request):

    payload = request.body
    sig_header = request.META.get("HTTP_STRIPE_SIGNATURE")

    try:
        event = stripe.Webhook.construct_event(
            payload,
            sig_header,
            settings.STRIPE_WEBHOOK_SECRET
        )
    except stripe.error.SignatureVerificationError:
        return HttpResponse(status=400)
    except Exception:
        return HttpResponse(status=400)

    event_type = event["type"]
    data = event["data"]["object"]

    # ======================================================
    # CHECKOUT COMPLETED
    # ======================================================
    if event_type == "checkout.session.completed":

        customer_id = data.get("customer")
        subscription_id = data.get("subscription")

        pharmacy = Pharmacy.objects.filter(
            stripe_customer_id=customer_id
        ).first()

        if pharmacy:
            pharmacy.stripe_subscription_id = subscription_id
            pharmacy.subscription_status = "active"
            pharmacy.is_active = True
            pharmacy.save()

    # ======================================================
    # SUBSCRIPTION UPDATED
    # ======================================================
    elif event_type == "customer.subscription.updated":

        subscription_id = data.get("id")
        status = data.get("status")
        period_end = data.get("current_period_end")

        pharmacy = Pharmacy.objects.filter(
            stripe_subscription_id=subscription_id
        ).first()

        if pharmacy:

            pharmacy.subscription_status = status

            if period_end:
                pharmacy.current_period_end = datetime.fromtimestamp(
                    period_end,
                    tz=timezone.utc
                )

            pharmacy.is_active = status in ["active", "trialing"]

            pharmacy.save()

    # ======================================================
    # SUBSCRIPTION DELETED / CANCELED
    # ======================================================
    elif event_type == "customer.subscription.deleted":

        subscription_id = data.get("id")

        pharmacy = Pharmacy.objects.filter(
            stripe_subscription_id=subscription_id
        ).first()

        if pharmacy:
            pharmacy.subscription_status = "canceled"
            pharmacy.is_active = False
            pharmacy.save()

    # ======================================================
    # PAYMENT FAILED
    # ======================================================
    elif event_type == "invoice.payment_failed":

        subscription_id = data.get("subscription")

        pharmacy = Pharmacy.objects.filter(
            stripe_subscription_id=subscription_id
        ).first()

        if pharmacy:
            pharmacy.subscription_status = "past_due"

            # 7 jours de grace period
            pharmacy.grace_until = timezone.now() + timezone.timedelta(days=7)

            pharmacy.save()

    # ======================================================
    # PAYMENT SUCCEEDED
    # ======================================================
    elif event_type == "invoice.payment_succeeded":

        subscription_id = data.get("subscription")

        pharmacy = Pharmacy.objects.filter(
            stripe_subscription_id=subscription_id
        ).first()

        if pharmacy:
            pharmacy.subscription_status = "active"
            pharmacy.grace_until = None
            pharmacy.is_active = True
            pharmacy.save()

    return HttpResponse(status=200)