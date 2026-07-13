from rest_framework.viewsets import ModelViewSet
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response

from core.permissions import can_manage_inventory
from core.permissions import IsInventoryManagerOrReadOnly


class BaseModelViewSet(ModelViewSet):
    permission_classes = (IsInventoryManagerOrReadOnly,)

    def get_queryset(self):
        queryset = super().get_queryset()
        include_inactive = self.request.query_params.get("include_inactive") == "true"

        if hasattr(queryset.model, "is_active"):
            if self.action == "restore":
                return queryset

            if include_inactive and can_manage_inventory(self.request.user):
                return queryset

            return queryset.filter(is_active=True)

        return queryset

    def perform_create(self, serializer):
        save_kwargs = {}

        if hasattr(serializer.Meta.model, "created_by"):
            save_kwargs["created_by"] = self.request.user
            save_kwargs["updated_by"] = self.request.user

        serializer.save(**save_kwargs)

    def perform_update(self, serializer):
        save_kwargs = {}

        if hasattr(serializer.Meta.model, "updated_by"):
            save_kwargs["updated_by"] = self.request.user

        serializer.save(**save_kwargs)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()

        if hasattr(instance, "deactivate"):
            instance.deactivate(user=request.user)
            return Response(status=status.HTTP_204_NO_CONTENT)

        return super().destroy(request, *args, **kwargs)

    @action(detail=True, methods=["post"], url_path="restore")
    def restore(self, request, pk=None):
        instance = self.get_object()

        if not hasattr(instance, "activate"):
            return Response(
                {"detail": "Bu kayit geri alinabilir yapida degil."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        instance.activate(user=request.user)
        serializer = self.get_serializer(instance)
        return Response(serializer.data)
