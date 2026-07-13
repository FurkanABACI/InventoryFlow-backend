from rest_framework import serializers


class BaseModelSerializer(serializers.ModelSerializer):
    created_by_username = serializers.CharField(
        source="created_by.username",
        read_only=True,
    )
    updated_by_username = serializers.CharField(
        source="updated_by.username",
        read_only=True,
    )

    class Meta:
        fields = (
            "id",
            "created_at",
            "updated_at",
            "created_by",
            "created_by_username",
            "updated_by",
            "updated_by_username",
            "is_active",
        )
        read_only_fields = (
            "id",
            "created_at",
            "updated_at",
            "created_by",
            "created_by_username",
            "updated_by",
            "updated_by_username",
        )
