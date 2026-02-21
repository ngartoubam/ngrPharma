# backend/core/api/stock/stock_entry_views.py

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions, status
from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema

from core.permissions import IsAdminOrGerant
from core.models import StockEntry

# ✅ IMPORT RELATIF CORRECT
from .serializers import (
    StockEntryCreateSerializer,
    StockEntryListSerializer,
    StockEntryDetailSerializer,
    StockEntryValidationSerializer,
)


# =========================================================
# CREATE STOCK ENTRY (Draft)
# =========================================================
class StockEntryCreateView(APIView):
    permission_classes = [
        permissions.IsAuthenticated,
        IsAdminOrGerant
    ]

    @extend_schema(
        request=StockEntryCreateSerializer,
        responses={201: StockEntryCreateSerializer},
        summary="Créer un bon d’entrée (brouillon)",
        description="Création d’un bon d’entrée en statut draft"
    )
    def post(self, request):
        serializer = StockEntryCreateSerializer(
            data=request.data,
            context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(
            {"detail": "Bon d’entrée créé en brouillon"},
            status=status.HTTP_201_CREATED
        )


# =========================================================
# LIST STOCK ENTRIES
# =========================================================
class StockEntryListView(APIView):
    permission_classes = [
        permissions.IsAuthenticated,
        IsAdminOrGerant
    ]

    @extend_schema(
        responses={200: StockEntryListSerializer(many=True)},
        summary="Liste des bons d’entrée",
        description="Retourne tous les bons d’entrée de la pharmacie"
    )
    def get(self, request):
        pharmacy = request.user.pharmacy

        entries = (
            StockEntry.objects
            .filter(pharmacy=pharmacy)
            .select_related("supplier")
            .order_by("-created_at")
        )

        serializer = StockEntryListSerializer(entries, many=True)
        return Response(serializer.data)


# =========================================================
# DETAIL STOCK ENTRY
# =========================================================
class StockEntryDetailView(APIView):
    permission_classes = [
        permissions.IsAuthenticated,
        IsAdminOrGerant
    ]

    @extend_schema(
        responses={200: StockEntryDetailSerializer},
        summary="Détail d’un bon d’entrée",
    )
    def get(self, request, pk):
        pharmacy = request.user.pharmacy

        entry = get_object_or_404(
            StockEntry,
            id=pk,
            pharmacy=pharmacy
        )

        serializer = StockEntryDetailSerializer(entry)
        return Response(serializer.data)


# =========================================================
# VALIDATE STOCK ENTRY (STEP 2 WORKFLOW)
# =========================================================
class StockEntryValidateView(APIView):
    permission_classes = [
        permissions.IsAuthenticated,
        IsAdminOrGerant
    ]

    @extend_schema(
        request=StockEntryValidationSerializer,
        responses={200: StockEntryDetailSerializer},
        summary="Valider un bon d’entrée",
        description="Validation officielle → création des lots ProductBatch"
    )
    def post(self, request, pk):
        pharmacy = request.user.pharmacy

        entry = get_object_or_404(
            StockEntry,
            id=pk,
            pharmacy=pharmacy
        )

        if entry.status == "validated":
            return Response(
                {"detail": "Bon déjà validé"},
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer = StockEntryValidationSerializer(
            entry,
            data=request.data,
            context={"request": request},
            partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(
            {"detail": "Bon d’entrée validé avec succès"},
            status=status.HTTP_200_OK
        )