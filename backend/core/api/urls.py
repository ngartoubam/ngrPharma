from django.urls import path

from core.api.auth_views import PinLoginView
from core.api.sale_views import CreateSaleView, SaleHistoryView
from core.api.sale_audit_views import SaleAuditLogListView
from core.api.dashboard_views import DashboardAlertsView

from core.api.stock_entry_views import (
    StockEntryCreateView,
    StockEntryListView,
    StockEntryDetailView,
    StockEntryValidateView,
)

from core.api.product_views import (
    ProductStockListView,
    LowStockProductListView,
    ProductExpiryAlertView,
    ExpiringSoonProductListView,
)

urlpatterns = [

    # 🔐 ================= AUTH =================
    path("auth/pin-login/", PinLoginView.as_view(), name="pin-login"),

    # 🧾 ================= SALES =================
    path("sales/create/", CreateSaleView.as_view(), name="sale-create"),
    path("sales/history/", SaleHistoryView.as_view(), name="sale-history"),

    # 🛑 ================= SALES AUDIT =================
    path("sales/audit/", SaleAuditLogListView.as_view(), name="sale-audit-log"),

    # 📦 ================= PRODUCTS =================
    path("products/stock/", ProductStockListView.as_view(), name="product-stock"),
    path("products/low-stock/", LowStockProductListView.as_view(), name="low-stock"),

    # ⏰ ================= EXPIRY ALERTS =================
    path("products/expiry-alerts/", ProductExpiryAlertView.as_view(), name="expiry-alerts"),
    path("products/expiring-soon/", ExpiringSoonProductListView.as_view(), name="expiring-soon"),

    # 📊 ================= DASHBOARD =================
    path("dashboard/alerts/", DashboardAlertsView.as_view(), name="dashboard-alerts"),

    # 📥 ================= STOCK ENTRIES =================
    path("stock-entries/create/", StockEntryCreateView.as_view(), name="stock-entry-create"),
    path("stock-entries/", StockEntryListView.as_view(), name="stock-entry-list"),
    path("stock-entries/<uuid:pk>/", StockEntryDetailView.as_view(), name="stock-entry-detail"),
    path("stock-entries/<uuid:pk>/validate/", StockEntryValidateView.as_view(), name="stock-entry-validate"),

]
