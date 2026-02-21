# backend/core/api/auth/urls.py

from django.urls import path
from .views import PinLoginView, AdminLoginView

urlpatterns = [
    path("pin-login/", PinLoginView.as_view(), name="pin-login"),
    path("admin-login/", AdminLoginView.as_view(), name="admin-login"),
]