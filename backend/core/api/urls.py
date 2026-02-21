# backend/core/api/urls.py

from django.urls import path, include

urlpatterns = [

    # ================= AUTH =================
    path("auth/", include("core.api.auth.urls")),

    # ================= SALES =================
    path("sales/", include("core.api.sales.urls")),

    # ================= PRODUCTS =================
    path("products/", include("core.api.products.urls")),

    # ================= STOCK =================
    path("stock/", include("core.api.stock.urls")),

    # ================= FINANCE =================
    path("finance/", include("core.api.finance.urls")),

    # ================= INTELLIGENCE =================
    path("intelligence/", include("core.api.intelligence.urls")),

    # ================= SaaS ADMIN =================
    path("admin/", include("core.api.admin.urls")),
]