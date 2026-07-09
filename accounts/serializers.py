from django.contrib.auth import authenticate
from django.contrib.auth.models import User

from rest_framework import serializers

from accounts.choices import UserRole
from accounts.models import UserProfile


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


class ManagedUserSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()
    role = serializers.ChoiceField(choices=UserRole.choices, write_only=True)
    role_value = serializers.SerializerMethodField()
    role_label = serializers.SerializerMethodField()
    department = serializers.CharField(required=False, allow_blank=True, write_only=True)
    department_value = serializers.SerializerMethodField()
    password = serializers.CharField(
        required=False,
        allow_blank=True,
        write_only=True,
        min_length=6,
    )
    can_manage_inventory = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            "id",
            "username",
            "first_name",
            "last_name",
            "full_name",
            "email",
            "is_active",
            "is_staff",
            "is_superuser",
            "role",
            "role_value",
            "role_label",
            "department",
            "department_value",
            "password",
            "can_manage_inventory",
        )
        read_only_fields = (
            "is_staff",
            "is_superuser",
            "role_value",
            "role_label",
            "department_value",
            "can_manage_inventory",
        )

    def get_full_name(self, obj):
        full_name = obj.get_full_name()
        return full_name or obj.username

    def get_role_value(self, obj):
        return UserSerializer().get_role(obj)

    def get_role_label(self, obj):
        return UserRole(self.get_role_value(obj)).label

    def get_department_value(self, obj):
        return UserSerializer().get_department(obj)

    def get_can_manage_inventory(self, obj):
        return self.get_role_value(obj) in (UserRole.ADMIN, UserRole.OPERATIONS)

    def validate_username(self, value):
        value = value.strip()

        if not value:
            raise serializers.ValidationError("Kullanici adi zorunludur.")

        return value

    def _set_role_fields(self, user, role, department):
        user.is_staff = role in (UserRole.ADMIN, UserRole.OPERATIONS)
        user.save(update_fields=["is_staff"])
        UserProfile.objects.update_or_create(
            user=user,
            defaults={
                "role": role,
                "department": department,
                "is_active": user.is_active,
            },
        )

    def create(self, validated_data):
        role = validated_data.pop("role")
        department = validated_data.pop("department", "")
        password = validated_data.pop("password", "")

        if not password:
            raise serializers.ValidationError({"password": "Sifre zorunludur."})

        user = User(**validated_data)
        user.set_password(password)
        user.save()
        self._set_role_fields(user, role, department)
        return user

    def update(self, instance, validated_data):
        role = validated_data.pop("role", self.get_role_value(instance))
        department = validated_data.pop("department", self.get_department_value(instance))
        password = validated_data.pop("password", "")

        for field, value in validated_data.items():
            setattr(instance, field, value)

        if password:
            instance.set_password(password)

        instance.save()
        self._set_role_fields(instance, role, department)
        return instance
