from rest_framework.viewsets import ModelViewSet

from core.permissions import IsAdminOrReadOnly


class BaseModelViewSet(ModelViewSet):
    permission_classes = (IsAdminOrReadOnly,)

    def get_queryset(self):
        queryset = super().get_queryset()

        if hasattr(queryset.model, "is_active"):
            return queryset.filter(is_active=True)

        return queryset
