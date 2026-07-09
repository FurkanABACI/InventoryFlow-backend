from django.db import transaction
from django.db.models import Q
from django.utils import timezone
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from catalog.models import Product
from core.permissions import can_manage_inventory, get_user_department
from core.views import BaseModelViewSet
from requisitions.choices import StockRequestStatus
from requisitions.models import StockRequest
from requisitions.serializers import StockRequestSerializer
from stock.choices import StockMovementType
from stock.models import StockMovement


class StockRequestViewSet(BaseModelViewSet):
    queryset = StockRequest.objects.select_related("requester_user").prefetch_related(
        "items__product"
    ).all()
    serializer_class = StockRequestSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        queryset = super().get_queryset()

        if can_manage_inventory(self.request.user):
            return queryset

        department = get_user_department(self.request.user)
        own_requests = Q(requester_user=self.request.user)

        if department:
            own_requests |= Q(department__iexact=department)

        return queryset.filter(own_requests)

    def perform_create(self, serializer):
        department = get_user_department(self.request.user)

        if not can_manage_inventory(self.request.user) and department:
            serializer.save(
                requester_user=self.request.user,
                department=department,
            )
            return

        serializer.save(requester_user=self.request.user)

    @action(detail=True, methods=["post"], url_path="fulfill")
    def fulfill(self, request, pk=None):
        if not can_manage_inventory(request.user):
            return Response(
                {"detail": "Bu talebi teslim etmek icin idari isler yetkisi gerekir."},
                status=status.HTTP_403_FORBIDDEN,
            )

        with transaction.atomic():
            stock_request = (
                StockRequest.objects.select_for_update()
                .prefetch_related("items__product")
                .get(pk=self.get_object().pk)
            )

            if stock_request.status == StockRequestStatus.FULFILLED:
                return Response(
                    {"detail": "Bu talep zaten teslim edilmis."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            if stock_request.status == StockRequestStatus.CANCELLED:
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
                stock_request.status = StockRequestStatus.PURCHASE_NEEDED
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
                    movement_type=StockMovementType.OUT,
                    quantity=item.quantity,
                    source_type="stock_request",
                    source_id=stock_request.id,
                    note=f"{stock_request.department} talebi teslim edildi",
                )

            stock_request.status = StockRequestStatus.FULFILLED
            stock_request.fulfilled_at = timezone.now()
            stock_request.save(update_fields=["status", "fulfilled_at", "updated_at"])

        serializer = self.get_serializer(stock_request)
        return Response(serializer.data)

    @action(detail=True, methods=["post"], url_path="cancel")
    def cancel(self, request, pk=None):
        stock_request = self.get_object()

        if (
            not can_manage_inventory(request.user)
            and stock_request.requester_user_id != request.user.id
        ):
            return Response(
                {"detail": "Sadece kendi talebinizi iptal edebilirsiniz."},
                status=status.HTTP_403_FORBIDDEN,
            )

        if stock_request.status == StockRequestStatus.FULFILLED:
            return Response(
                {"detail": "Teslim edilen talep iptal edilemez."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        stock_request.status = StockRequestStatus.CANCELLED
        stock_request.save(update_fields=["status", "updated_at"])
        serializer = self.get_serializer(stock_request)
        return Response(serializer.data)
