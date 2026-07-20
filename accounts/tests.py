from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.test import APITestCase

from accounts.choices import UserRole
from accounts.models import UserProfile


class ManagedUserTests(APITestCase):
    def setUp(self):
        self.admin_user = User.objects.create_user(
            username="admin",
            password="testpass123",
            is_staff=True,
        )
        UserProfile.objects.create(user=self.admin_user, role=UserRole.ADMIN)

        self.managed_user = User.objects.create_user(
            username="personel",
            password="testpass123",
            is_active=False,
        )
        UserProfile.objects.create(
            user=self.managed_user,
            role=UserRole.DEPARTMENT,
            department="Yemekhane",
            is_active=False,
        )

    def test_admin_can_activate_inactive_user(self):
        self.client.force_authenticate(self.admin_user)

        response = self.client.patch(
            f"/api/auth/users/{self.managed_user.id}/",
            {
                "is_active": True,
                "role": UserRole.DEPARTMENT,
                "department": "Yemekhane",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.managed_user.refresh_from_db()
        self.managed_user.profile.refresh_from_db()

        self.assertTrue(self.managed_user.is_active)
        self.assertTrue(self.managed_user.profile.is_active)

    def test_non_admin_cannot_manage_users(self):
        department_user = User.objects.create_user(
            username="talepci",
            password="testpass123",
        )
        UserProfile.objects.create(
            user=department_user,
            role=UserRole.DEPARTMENT,
            department="Yemekhane",
        )
        self.client.force_authenticate(department_user)

        response = self.client.get("/api/auth/users/")

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
