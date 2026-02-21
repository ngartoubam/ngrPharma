from django.urls import path
from .views import (
    AdminOverviewView,
    AdminPharmacyListCreateView,
    AdminPharmacyDetailView,
    AdminPharmacyActivateView,
    AdminPharmacySuspendView,
    AdminSubscriptionsListView,
)

urlpatterns = [
    path("overview/", AdminOverviewView.as_view(), name="admin-overview"),
    path("pharmacies/", AdminPharmacyListCreateView.as_view(), name="admin-pharmacies"),
    path("pharmacies/<uuid:pk>/", AdminPharmacyDetailView.as_view(), name="admin-pharmacy-detail"),

    # Actions
    path("pharmacies/<uuid:pk>/activate/", AdminPharmacyActivateView.as_view(), name="admin-pharmacy-activate"),
    path("pharmacies/<uuid:pk>/suspend/", AdminPharmacySuspendView.as_view(), name="admin-pharmacy-suspend"),
    path("subscriptions/", AdminSubscriptionsListView.as_view(), name="admin-subscriptions"),
]