from django.db import transaction
from django.utils import timezone
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response

from catalog.models import Product
from core.views import BaseModelViewSet
from requisitions.models import StockRequest
from requisitions.serializers import StockRequestSerializer
from stock.models import StockMovement


class StockRequestViewSet(BaseModelViewSet):
    queryset = StockRequest.objects.prefetch_related("items__product").all()
    serializer_class = StockRequestSerializer

    @action(detail=True, methods=["post"], url_path="fulfill")
    def fulfill(self, request, pk=None):
        with transaction.atomic():
            stock_request = (
                StockRequest.objects.select_for_update()
                .prefetch_related("items__product")
                .get(pk=self.get_object().pk)
            )

            if stock_request.status == StockRequest.Status.FULFILLED:
                return Response(
                    {"detail": "Bu talep zaten teslim edilmis."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            if stock_request.status == StockRequest.Status.CANCELLED:
                return Response(
                    {"detail": "Iptal edilen talep teslim edilemez."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            shortages = []

            for item in stock_request.items.all():
                product = Product.objects.select_for_update().get(id=item.product_id)

                if product.stock < item.quantity:
                    shortages.append(
                        {
                            "product": product.id,
                            "product_name": product.name,
                            "requested": item.quantity,
                            "available": product.stock,
                        }
                    )

            if shortages:
                stock_request.status = StockRequest.Status.PURCHASE_NEEDED
                stock_request.save(update_fields=["status", "updated_at"])
                serializer = self.get_serializer(stock_request)
                return Response(
                    {
                        "detail": "Stok yetersiz. Talep tedarik bekliyor durumuna alindi.",
                        "shortages": shortages,
                        "request": serializer.data,
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            for item in stock_request.items.all():
                product = Product.objects.select_for_update().get(id=item.product_id)
                product.stock -= item.quantity
                product.save(update_fields=["stock", "updated_at"])
                item.delivered_quantity = item.quantity
                item.save(update_fields=["delivered_quantity", "updated_at"])
                StockMovement.objects.create(
                    product=product,
                    movement_type=StockMovement.MovementType.OUT,
                    quantity=item.quantity,
                    source_type="stock_request",
                    source_id=stock_request.id,
                    note=f"{stock_request.department} talebi teslim edildi",
                )

            stock_request.status = StockRequest.Status.FULFILLED
            stock_request.fulfilled_at = timezone.now()
            stock_request.save(update_fields=["status", "fulfilled_at", "updated_at"])

        serializer = self.get_serializer(stock_request)
        return Response(serializer.data)

    @action(detail=True, methods=["post"], url_path="cancel")
    def cancel(self, request, pk=None):
        stock_request = self.get_object()

        if stock_request.status == StockRequest.Status.FULFILLED:
            return Response(
                {"detail": "Teslim edilen talep iptal edilemez."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        stock_request.status = StockRequest.Status.CANCELLED
        stock_request.save(update_fields=["status", "updated_at"])
        serializer = self.get_serializer(stock_request)
        return Response(serializer.data)
