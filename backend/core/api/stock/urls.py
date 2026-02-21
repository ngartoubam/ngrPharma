# backend/core/api/stock/urls.py

from django.urls import path

from .stock_entry_views import (
    StockEntryCreateView,
    StockEntryListView,
    StockEntryDetailView,
    StockEntryValidateView,
)

urlpatterns = [
    path("create/", StockEntryCreateView.as_view(), name="stock-entry-create"),
    path("", StockEntryListView.as_view(), name="stock-entry-list"),
    path("<uuid:pk>/", StockEntryDetailView.as_view(), name="stock-entry-detail"),
    path("<uuid:pk>/validate/", StockEntryValidateView.as_view(), name="stock-entry-validate"),
]