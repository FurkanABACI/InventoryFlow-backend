from django.contrib.auth import authenticate

from rest_framework import serializers

from accounts.choices import UserRole


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        username = attrs.get("username")
        password = attrs.get("password")

        user = authenticate(username=username, password=password)

        if not user:
            raise serializers.ValidationError("Kullanici adi veya sifre hatali.")

        if not user.is_active:
            raise serializers.ValidationError("Bu kullanici pasif durumdadir.")

        attrs["user"] = user
        return attrs


class UserSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    username = serializers.CharField(read_only=True)
    email = serializers.EmailField(read_only=True)
    is_staff = serializers.BooleanField(read_only=True)
    is_superuser = serializers.BooleanField(read_only=True)
    full_name = serializers.SerializerMethodField()
    role = serializers.SerializerMethodField()
    role_label = serializers.SerializerMethodField()
    department = serializers.SerializerMethodField()
    can_manage_inventory = serializers.SerializerMethodField()

    def _get_profile(self, obj):
        return getattr(obj, "profile", None)

    def get_full_name(self, obj):
        full_name = obj.get_full_name()
        return full_name or obj.username

    def get_role(self, obj):
        if obj.is_superuser:
            return UserRole.ADMIN

        profile = self._get_profile(obj)

        if profile:
            return profile.role

        if obj.is_staff:
            return UserRole.OPERATIONS

        return UserRole.DEPARTMENT

    def get_role_label(self, obj):
        return UserRole(self.get_role(obj)).label

    def get_department(self, obj):
        profile = self._get_profile(obj)
        return profile.department if profile else ""

    def get_can_manage_inventory(self, obj):
        return self.get_role(obj) in (UserRole.ADMIN, UserRole.OPERATIONS)
