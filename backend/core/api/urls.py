from django.urls import path
from core.api.auth_views import PinLoginView
from core.api.sale_views import CreateSaleView, SaleHistoryView  # ICI

urlpatterns = [
    # Auth
    path("auth/pin-login/", PinLoginView.as_view(), name="pin-login"),

    # Sales
    path("sales/create/", CreateSaleView.as_view(), name="sale-create"),
    path("sales/history/", SaleHistoryView.as_view(), name="sale-history"),
]
