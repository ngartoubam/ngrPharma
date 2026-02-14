import csv
from datetime import datetime

from django.http import HttpResponse

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import IsAuthenticated

from drf_spectacular.utils import extend_schema

from core.models import SaleAuditLog
from core.api.sale_audit_serializers import SaleAuditLogSerializer
from core.permissions import IsAdminOrGerant


# ======================================================
# PAGINATION
# ======================================================
class SaleAuditLogPagination(LimitOffsetPagination):
    default_limit = 20
    max_limit = 100


# ======================================================
# VIEW
# ======================================================
class SaleAuditLogListView(APIView):
    """
    Consultation et export du journal d’audit des ventes
    """
    permission_classes = [IsAuthenticated, IsAdminOrGerant]
    pagination_class = SaleAuditLogPagination

    @extend_schema(
        responses={200: SaleAuditLogSerializer(many=True)},
        summary="Journal d’audit des ventes",
        description="Consultation, filtres et export CSV / Excel (admin uniquement)",
    )
    def get(self, request):
        user = request.user
        pharmacy = user.pharmacy

        qs = SaleAuditLog.objects.filter(pharmacy=pharmacy)

        # -------------------------------------------------
        # 🔍 FILTRES
        # -------------------------------------------------
        reason = request.GET.get("reason")
        product = request.GET.get("product")
        date_from = request.GET.get("date_from")
        date_to = request.GET.get("date_to")

        if reason:
            qs = qs.filter(reason=reason)

        if product:
            qs = qs.filter(product_id=product)

        if date_from:
            qs = qs.filter(created_at__date__gte=date_from)

        if date_to:
            qs = qs.filter(created_at__date__lte=date_to)

        qs = qs.select_related("product", "user").order_by("-created_at")

        # -------------------------------------------------
        # 📤 EXPORT (ADMIN UNIQUEMENT)
        # -------------------------------------------------
        export = request.GET.get("export")

        if export:
            if user.role != "admin":
                return Response(
                    {"detail": "Seul l’administrateur peut exporter le journal d’audit"},
                    status=status.HTTP_403_FORBIDDEN,
                )

            if export == "csv":
                return self._export_csv(qs)

            if export == "xlsx":
                return self._export_excel(qs)

        # -------------------------------------------------
        # 📄 JSON PAGINÉ
        # -------------------------------------------------
        paginator = self.pagination_class()
        page = paginator.paginate_queryset(qs, request)

        serializer = SaleAuditLogSerializer(page, many=True)
        return paginator.get_paginated_response(serializer.data)

    # ======================================================
    # CSV EXPORT
    # ======================================================
    def _export_csv(self, queryset):
        response = HttpResponse(content_type="text/csv")
        response["Content-Disposition"] = 'attachment; filename="sale_audit_log.csv"'

        writer = csv.writer(response)
        writer.writerow([
            "Date",
            "Utilisateur",
            "Produit",
            "Quantité demandée",
            "Raison",
            "Message",
        ])

        for log in queryset:
            writer.writerow([
                log.created_at.strftime("%Y-%m-%d %H:%M"),
                log.user.name if log.user else "",
                log.product.name if log.product else "",
                log.requested_quantity,
                log.reason,
                log.message,
            ])

        return response

    # ======================================================
    # EXCEL EXPORT
    # ======================================================
    def _export_excel(self, queryset):
        try:
            import openpyxl
        except ImportError:
            return Response(
                {"detail": "openpyxl non installé"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "Audit ventes"

        headers = [
            "Date",
            "Utilisateur",
            "Produit",
            "Quantité demandée",
            "Raison",
            "Message",
        ]
        ws.append(headers)

        for log in queryset:
            ws.append([
                log.created_at.strftime("%Y-%m-%d %H:%M"),
                log.user.name if log.user else "",
                log.product.name if log.product else "",
                log.requested_quantity,
                log.reason,
                log.message,
            ])

        response = HttpResponse(
            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
        response["Content-Disposition"] = 'attachment; filename="sale_audit_log.xlsx"'
        wb.save(response)

        return response
