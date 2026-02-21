# backend/core/api/sales/urls.py

from django.urls import path

from .views import CreateSaleView, SaleHistoryView
from .sale_audit_views import SaleAuditLogListView

urlpatterns = [
    path("create/", CreateSaleView.as_view(), name="sale-create"),
    path("history/", SaleHistoryView.as_view(), name="sale-history"),
    path("audit/", SaleAuditLogListView.as_view(), name="sale-audit-log"),
]