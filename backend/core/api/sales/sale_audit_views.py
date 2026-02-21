# backend/core/api/sales/sale_audit_views.py

from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema

from core.models import SaleAuditLog
from .serializers import SaleAuditLogSerializer


class SaleAuditLogListView(ListAPIView):
    """
    Journal d’audit des ventes pour la pharmacie connectée
    """
    permission_classes = [IsAuthenticated]
    serializer_class = SaleAuditLogSerializer

    @extend_schema(
        summary="Journal d’audit des ventes",
        description="Retourne l’historique des ventes bloquées et réussies pour la pharmacie connectée",
        responses=SaleAuditLogSerializer(many=True),
    )
    def get_queryset(self):
        return (
            SaleAuditLog.objects
            .filter(pharmacy=self.request.user.pharmacy)
            .select_related("product", "user")
            .order_by("-created_at")
        )