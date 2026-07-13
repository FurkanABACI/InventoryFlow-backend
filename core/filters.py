import django_filters
from django.db.models import Q


class BaseFilterSet(django_filters.FilterSet):
    is_active = django_filters.BooleanFilter(field_name="is_active")
    created_after = django_filters.DateTimeFilter(
        field_name="created_at",
        lookup_expr="gte",
    )
    created_before = django_filters.DateTimeFilter(
        field_name="created_at",
        lookup_expr="lte",
    )
    updated_after = django_filters.DateTimeFilter(
        field_name="updated_at",
        lookup_expr="gte",
    )
    updated_before = django_filters.DateTimeFilter(
        field_name="updated_at",
        lookup_expr="lte",
    )
    search = django_filters.CharFilter(method="filter_search")

    search_fields = ()

    def filter_search(self, queryset, name, value):
        search_value = value.strip()

        if not search_value or not self.search_fields:
            return queryset

        query = Q()

        for field in self.search_fields:
            query |= Q(**{f"{field}__icontains": search_value})

        return queryset.filter(query)
