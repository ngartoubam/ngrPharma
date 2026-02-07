from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions, status
from drf_spectacular.utils import extend_schema

from core.api.sale_serializers import SaleCreateSerializer


class CreateSaleView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(
        request=SaleCreateSerializer,
        responses={201: None},
    )
    def post(self, request):
        serializer = SaleCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        sale = serializer.save()

        return Response(
            {
                "sale_id": str(sale.id),
                "total": sale.total_price,
            },
            status=status.HTTP_201_CREATED,
        )
