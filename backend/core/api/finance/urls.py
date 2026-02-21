# core/api/finance/urls.py

from django.urls import path
from .views import (
    FinanceDashboardView,
    FinanceMonthlyView,
    FinanceTopProductsView,
    StockRotationView,
)

urlpatterns = [
    path("dashboard/", FinanceDashboardView.as_view(), name="finance-dashboard"),
    path("monthly/", FinanceMonthlyView.as_view(), name="finance-monthly"),
    path("top-products/", FinanceTopProductsView.as_view(), name="finance-top-products"),
    path("stock-rotation/", StockRotationView.as_view(), name="finance-stock-rotation"),
]