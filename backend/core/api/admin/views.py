# backend/core/api/admin/views.py

from datetime import timedelta

from django.db.models import Sum, Count
from django.utils import timezone
from django.shortcuts import get_object_or_404


from rest_framework.views import APIView

from rest_framework.permissions import IsAuthenticated


from core.models import Pharmacy
from core.permissions import IsSaaSAdmin


from rest_framework import permissions, status, serializers
from rest_framework.generics import (
    GenericAPIView,
    ListCreateAPIView,
    RetrieveUpdateDestroyAPIView,
)
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema

from core.models import Pharmacy, Sale, CustomUser
from core.permissions import IsSaaSAdmin
from .serializers import AdminPharmacySerializer


# =========================================================
# 🔧 ACTION SERIALIZER
# =========================================================
class AdminPharmacySuspendSerializer(serializers.Serializer):
    suspended_reason = serializers.CharField(required=False, allow_blank=True)


# =========================================================
# 📊 ADMIN OVERVIEW (GLOBAL DASHBOARD ENTERPRISE)
# =========================================================
class AdminOverviewView(GenericAPIView):

    permission_classes = [permissions.IsAuthenticated, IsSaaSAdmin]
    serializer_class = AdminPharmacySerializer  # schema clean

    @extend_schema(summary="SaaS Admin Global Overview Dashboard")
    def get(self, request):

        now = timezone.now()
        thirty_days_ago = now - timedelta(days=30)

        # ---------------------------
        # PHARMACIES
        # ---------------------------
        total_pharmacies = Pharmacy.objects.count()
        new_pharmacies = Pharmacy.objects.filter(
            created_at__gte=thirty_days_ago
        ).count()

        pharmacies_by_type = (
            Pharmacy.objects.values("type")
            .annotate(count=Count("id"))
        )

        pharmacies_by_country = (
            Pharmacy.objects.values("country")
            .annotate(count=Count("id"))
        )

        pharmacies_by_plan = (
            Pharmacy.objects.values("plan")
            .annotate(count=Count("id"))
        )

        pharmacies_by_subscription_status = (
            Pharmacy.objects.values("subscription_status")
            .annotate(count=Count("id"))
        )

        # ---------------------------
        # REVENUE
        # ---------------------------
        start_of_month = now.replace(
            day=1, hour=0, minute=0, second=0, microsecond=0
        )

        monthly_revenue = (
            Sale.objects.filter(created_at__gte=start_of_month)
            .aggregate(total=Sum("total_price"))
            .get("total") or 0
        )

        revenue_30_days = (
            Sale.objects.filter(created_at__gte=thirty_days_ago)
            .aggregate(total=Sum("total_price"))
            .get("total") or 0
        )

        sixty_days_ago = now - timedelta(days=60)

        previous_30_days_revenue = (
            Sale.objects.filter(
                created_at__gte=sixty_days_ago,
                created_at__lt=thirty_days_ago,
            )
            .aggregate(total=Sum("total_price"))
            .get("total") or 0
        )

        if previous_30_days_revenue > 0:
            revenue_growth_pct = (
                (revenue_30_days - previous_30_days_revenue)
                / previous_30_days_revenue
            ) * 100
        else:
            revenue_growth_pct = 100 if revenue_30_days > 0 else 0

        # ---------------------------
        # USERS
        # ---------------------------
        total_users = CustomUser.objects.count()
        total_admins = CustomUser.objects.filter(role="admin").count()
        total_gerants = CustomUser.objects.filter(role="gerant").count()

        # ---------------------------
        # SUBSCRIPTIONS SNAPSHOT
        # ---------------------------
        active_subscriptions = Pharmacy.objects.filter(
            subscription_status="active",
            is_active=True
        ).count()

        trialing_subscriptions = Pharmacy.objects.filter(
            subscription_status="trialing"
        ).count()

        past_due_subscriptions = Pharmacy.objects.filter(
            subscription_status="past_due"
        ).count()

        canceled_subscriptions = Pharmacy.objects.filter(
            subscription_status="canceled"
        ).count()

        return Response({

            "pharmacies": {
                "total": total_pharmacies,
                "new_last_30_days": new_pharmacies,
                "by_type": list(pharmacies_by_type),
                "by_country": list(pharmacies_by_country),
                "by_plan": list(pharmacies_by_plan),
                "by_subscription_status": list(pharmacies_by_subscription_status),
            },

            "revenue": {
                "current_month": float(monthly_revenue),
                "last_30_days": float(revenue_30_days),
                "previous_30_days": float(previous_30_days_revenue),
                "growth_percent": round(revenue_growth_pct, 2),
            },

            "users": {
                "total": total_users,
                "admins": total_admins,
                "gerants": total_gerants,
            },

            "subscriptions": {
                "active": active_subscriptions,
                "trialing": trialing_subscriptions,
                "past_due": past_due_subscriptions,
                "canceled": canceled_subscriptions,
            }
        })


# =========================================================
# 🏢 ADMIN PHARMACY LIST + CREATE
# =========================================================
class AdminPharmacyListCreateView(ListCreateAPIView):

    permission_classes = [permissions.IsAuthenticated, IsSaaSAdmin]
    queryset = Pharmacy.objects.all().order_by("-created_at")
    serializer_class = AdminPharmacySerializer


# =========================================================
# 🏢 ADMIN PHARMACY DETAIL
# =========================================================
class AdminPharmacyDetailView(RetrieveUpdateDestroyAPIView):

    permission_classes = [permissions.IsAuthenticated, IsSaaSAdmin]
    queryset = Pharmacy.objects.all()
    serializer_class = AdminPharmacySerializer


# =========================================================
# ✅ ACTIVATE PHARMACY
# =========================================================
class AdminPharmacyActivateView(GenericAPIView):

    permission_classes = [permissions.IsAuthenticated, IsSaaSAdmin]
    serializer_class = AdminPharmacySerializer

    @extend_schema(
        summary="Activate pharmacy (SaaS Admin)",
        operation_id="admin_pharmacy_activate",
    )
    def post(self, request, pk):

        pharmacy = get_object_or_404(Pharmacy, pk=pk)

        pharmacy.is_active = True
        pharmacy.suspended_reason = None
        pharmacy.save(update_fields=["is_active", "suspended_reason"])

        return Response(
            AdminPharmacySerializer(pharmacy).data,
            status=status.HTTP_200_OK
        )


# =========================================================
# 🚫 SUSPEND PHARMACY
# =========================================================
class AdminPharmacySuspendView(GenericAPIView):

    permission_classes = [permissions.IsAuthenticated, IsSaaSAdmin]
    serializer_class = AdminPharmacySuspendSerializer

    @extend_schema(
        request=AdminPharmacySuspendSerializer,
        summary="Suspend pharmacy (SaaS Admin)",
        operation_id="admin_pharmacy_suspend",
    )
    def post(self, request, pk):

        pharmacy = get_object_or_404(Pharmacy, pk=pk)

        serializer = self.get_serializer(data=request.data or {})
        serializer.is_valid(raise_exception=True)

        reason = (
            serializer.validated_data.get("suspended_reason")
            or "Suspended by SaaS admin"
        )

        pharmacy.is_active = False
        pharmacy.suspended_reason = reason
        pharmacy.save(update_fields=["is_active", "suspended_reason"])

        return Response(
            AdminPharmacySerializer(pharmacy).data,
            status=status.HTTP_200_OK
        )
        


# =====================================================
# SAAS ADMIN - SUBSCRIPTIONS LIST
# =====================================================
class AdminSubscriptionsListView(APIView):
    permission_classes = [IsAuthenticated, IsSaaSAdmin]

    def get(self, request):
        pharmacies = Pharmacy.objects.all().order_by("-created_at")

        data = []
        total_revenue = 0

        for p in pharmacies:
            monthly_price = 0

            if p.plan == "basic":
                monthly_price = 15000
            elif p.plan == "pro":
                monthly_price = 25000
            elif p.plan == "enterprise":
                monthly_price = 50000

            if p.subscription_status in ["active", "trialing"]:
                total_revenue += monthly_price

            data.append({
                "id": str(p.id),
                "name": p.name,
                "plan": p.plan,
                "status": p.subscription_status,
                "is_active": p.is_active,
                "current_period_end": p.current_period_end,
                "monthly_amount": monthly_price,
                "stripe_customer_id": p.stripe_customer_id,
            })

        return Response({
            "stats": {
                "total": pharmacies.count(),
                "active": pharmacies.filter(subscription_status="active").count(),
                "trialing": pharmacies.filter(subscription_status="trialing").count(),
                "past_due": pharmacies.filter(subscription_status="past_due").count(),
                "canceled": pharmacies.filter(subscription_status="canceled").count(),
                "mrr": total_revenue,
            },
            "subscriptions": data
        })