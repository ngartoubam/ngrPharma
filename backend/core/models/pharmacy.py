import uuid
from django.db import models
from django.utils import timezone


class Pharmacy(models.Model):
    PHARMACY_TYPES = (
        ("pharmacie", "Pharmacie"),
        ("depot", "Dépôt"),
    )

    # Stripe / Billing statuses (aligné avec Stripe)
    SUBSCRIPTION_STATUS = (
        ("inactive", "Inactive"),
        ("trialing", "Trialing"),
        ("active", "Active"),
        ("past_due", "Past Due"),
        ("canceled", "Canceled"),
        ("unpaid", "Unpaid"),
        ("incomplete", "Incomplete"),
        ("incomplete_expired", "Incomplete Expired"),
        ("paused", "Paused"),
    )

    PLAN_CHOICES = (
        ("starter", "Starter"),
        ("pro", "Pro"),
        ("enterprise", "Enterprise"),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    code = models.CharField(
        max_length=10,
        unique=True,
        blank=True,
        null=True
    )

    # ==========
    # Infos de base
    # ==========
    name = models.CharField(max_length=150)
    type = models.CharField(max_length=20, choices=PHARMACY_TYPES)

    # ✅ NOUVEAU : pays (multi-pays SaaS)
    # country = models.CharField(max_length=80, blank=True, null=True)
    country = models.CharField(max_length=100, default="Chad")

    city = models.CharField(max_length=100, blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now)

    # ==========
    # SaaS / Activation
    # ==========
    is_active = models.BooleanField(default=True)
    suspended_reason = models.CharField(max_length=255, blank=True, null=True)

    # ==========
    # Stripe Billing (Customer + Subscription)
    # ==========
    stripe_customer_id = models.CharField(max_length=255, blank=True, null=True)
    stripe_subscription_id = models.CharField(max_length=255, blank=True, null=True)

    plan = models.CharField(max_length=20, choices=PLAN_CHOICES, default="starter")

    subscription_status = models.CharField(
        max_length=30,
        choices=SUBSCRIPTION_STATUS,
        default="inactive"
    )

    current_period_end = models.DateTimeField(blank=True, null=True)

    stripe_price_id = models.CharField(max_length=255, blank=True, null=True)

    grace_until = models.DateTimeField(blank=True, null=True)

    # ==========
    # Utils
    # ==========
    def save(self, *args, **kwargs):
        if not self.code:
            self.code = self.generate_code()
        super().save(*args, **kwargs)

    def generate_code(self):
        import random
        return f"PH{random.randint(1000, 9999)}"

    def has_active_subscription(self):
        """
        Active/trialing = OK.
        Si grace_until est défini, on autorise jusqu'à cette date.
        """
        if not self.is_active:
            return False

        if self.subscription_status in ("active", "trialing"):
            return True

        if self.grace_until and self.grace_until >= timezone.now():
            return True

        return False

    def __str__(self):
        c = f" - {self.country}" if self.country else ""
        return f"{self.name} ({self.code}){c}"