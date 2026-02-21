# core/api/admin/views.py

from rest_framework.generics import (
    GenericAPIView,
    ListCreateAPIView,
    RetrieveUpdateDestroyAPIView,
)
from rest_framework.response import Response
from rest_framework import permissions
from drf_spectacular.utils import extend_schema

from django.utils import timezone
from datetime import timedelta
from django.db.models import Sum, Count

from core.models import Pharmacy, Sale, CustomUser
from core.permissions import IsSaaSAdmin
from .serializers import AdminPharmacySerializer


# =========================================================
# 📊 ADMIN OVERVIEW (GLOBAL DASHBOARD)
# =========================================================
class AdminOverviewView(GenericAPIView):
    """
    Dashboard global SaaS Admin
    """
    permission_classes = [permissions.IsAuthenticated, IsSaaSAdmin]
    serializer_class = AdminPharmacySerializer  # requis pour schema clean

    @extend_schema(summary="SaaS Admin Overview Dashboard")
    def get(self, request):

        now = timezone.now()

        # PHARMACIES
        total_pharmacies = Pharmacy.objects.count()
        thirty_days_ago = now - timedelta(days=30)

        new_pharmacies = Pharmacy.objects.filter(
            created_at__gte=thirty_days_ago
        ).count()

        pharmacies_by_type = (
            Pharmacy.objects
            .values("type")
            .annotate(count=Count("id"))
        )

        # REVENUE
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

        # USERS
        total_users = CustomUser.objects.count()
        total_admins = CustomUser.objects.filter(role="admin").count()
        total_gerants = CustomUser.objects.filter(role="gerant").count()

        return Response({
            "total_pharmacies": total_pharmacies,
            "new_pharmacies": new_pharmacies,
            "monthly_revenue": float(monthly_revenue),
            "active_subscriptions": total_pharmacies,

            "pharmacies": {
                "total": total_pharmacies,
                "new_last_30_days": new_pharmacies,
                "by_type": list(pharmacies_by_type),
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
                "active": total_pharmacies,
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