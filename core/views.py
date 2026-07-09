from rest_framework.viewsets import ModelViewSet

from core.permissions import IsInventoryManagerOrReadOnly


class BaseModelViewSet(ModelViewSet):
    permission_classes = (IsInventoryManagerOrReadOnly,)

    def get_queryset(self):
        queryset = super().get_queryset()

        if hasattr(queryset.model, "is_active"):
            return queryset.filter(is_active=True)

        return queryset
