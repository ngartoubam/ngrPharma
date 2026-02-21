# backend/core/api/products/urls.py

from django.urls import path

from .views import (
    ProductStockListView,
    LowStockProductListView,
    ProductExpiryAlertView,
)

urlpatterns = [
    path("stock/", ProductStockListView.as_view(), name="product-stock"),
    path("low-stock/", LowStockProductListView.as_view(), name="low-stock"),
    path("expiry-alerts/", ProductExpiryAlertView.as_view(), name="expiry-alerts"),
]