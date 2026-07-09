from rest_framework import serializers


class BaseModelSerializer(serializers.ModelSerializer):
    class Meta:
        fields = (
            "id",
            "created_at",
            "updated_at",
            "is_active",
        )
        read_only_fields = (
            "id",
            "created_at",
            "updated_at",
        )
