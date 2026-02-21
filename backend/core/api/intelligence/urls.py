# backend/core/api/intelligence/urls.py

from django.urls import path
from .views import IntelligenceView

urlpatterns = [
    path("overview/", IntelligenceView.as_view(), name="intelligence-overview"),
]