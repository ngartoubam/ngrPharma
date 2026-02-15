# backend/core/api/urls.py

from django.urls import path

# ================= AUTH =================
from core.api.auth_views import PinLoginView, EmailLoginView

# ================= SALES =================
from core.api.sale_views import CreateSaleView, SaleHistoryView
from core.api.sale_audit_views import SaleAuditLogListView

# ================= DASHBOARD =================
from core.api.dashboard_views import DashboardAlertsView

# ================= PRODUCTS =================
from core.api.product_views import (
    ProductStockListView,
    LowStockProductListView,
    ProductExpiryAlertView,
)

# ================= STOCK ENTRIES =================
from core.api.stock_entry_views import (
    StockEntryCreateView,
    StockEntryListView,
    StockEntryDetailView,
    StockEntryValidateView,
)

# ================= BUSINESS INTELLIGENCE =================
from core.api.finance_views import (
    FinanceDashboardView,
    MonthlyFinanceView,
    StockRotationView,
)

from core.api.intelligence_views import IntelligenceView


urlpatterns = [

    # 🔐 ================= AUTH =================
    path("auth/pin-login/", PinLoginView.as_view(), name="pin-login"),
    path("auth/login/", EmailLoginView.as_view(), name="email-login"),

    # 🧾 ================= SALES =================
    path("sales/create/", CreateSaleView.as_view(), name="sale-create"),
    path("sales/history/", SaleHistoryView.as_view(), name="sale-history"),

    # 🛑 ================= SALES AUDIT =================
    path("sales/audit/", SaleAuditLogListView.as_view(), name="sale-audit-log"),

    # 📦 ================= PRODUCTS =================
    path("products/stock/", ProductStockListView.as_view(), name="product-stock"),
    path("products/low-stock/", LowStockProductListView.as_view(), name="low-stock"),
    path("products/expiry-alerts/", ProductExpiryAlertView.as_view(), name="expiry-alerts"),

    # 📊 ================= DASHBOARD ALERTS =================
    path("dashboard/alerts/", DashboardAlertsView.as_view(), name="dashboard-alerts"),

    # 📥 ================= STOCK ENTRIES =================
    path("stock-entries/create/", StockEntryCreateView.as_view(), name="stock-entry-create"),
    path("stock-entries/", StockEntryListView.as_view(), name="stock-entry-list"),
    path("stock-entries/<uuid:pk>/", StockEntryDetailView.as_view(), name="stock-entry-detail"),
    path("stock-entries/<uuid:pk>/validate/", StockEntryValidateView.as_view(), name="stock-entry-validate"),

    # 📊 ================= BUSINESS INTELLIGENCE =================
    path("bi/finance/", FinanceDashboardView.as_view(), name="bi-finance"),
    path("bi/finance/monthly/", MonthlyFinanceView.as_view(), name="bi-finance-monthly"),
    path("bi/stock-rotation/", StockRotationView.as_view(), name="bi-stock-rotation"),
    path("bi/intelligence/", IntelligenceView.as_view(), name="bi-intelligence"),
]
