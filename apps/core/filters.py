import django_filters


class BaseFilterSet(django_filters.FilterSet):
    is_active = django_filters.BooleanFilter(field_name="is_active")
