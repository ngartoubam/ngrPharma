from django.urls import path
from core.api.auth_views import PinLoginView
from core.api.sale_views import CreateSaleView

urlpatterns = [
    path("auth/pin-login/", PinLoginView.as_view()),
]



urlpatterns += [
    path("sales/create/", CreateSaleView.as_view()),
]
