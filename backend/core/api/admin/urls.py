# backend/core/api/admin/urls.py

from django.urls import path
from .views import (
    AdminOverviewView,
    AdminPharmacyListCreateView,
    AdminPharmacyDetailView,
)

urlpatterns = [
    path("overview/", AdminOverviewView.as_view(), name="admin-overview"),
    path("pharmacies/", AdminPharmacyListCreateView.as_view(), name="admin-pharmacies"),
    path("pharmacies/<uuid:pk>/", AdminPharmacyDetailView.as_view(), name="admin-pharmacy-detail"),
]