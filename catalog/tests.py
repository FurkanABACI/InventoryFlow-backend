from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.test import APITestCase

from accounts.choices import UserRole
from accounts.models import UserProfile
from catalog.models import Category, Product, Supplier


class BaseViewSetBehaviorTests(APITestCase):
    def setUp(self):
        self.admin_user = User.objects.create_user(
            username="admin",
            password="testpass123",
            is_staff=True,
        )
        UserProfile.objects.create(user=self.admin_user, role=UserRole.ADMIN)
        self.client.force_authenticate(self.admin_user)

        self.category = Category.objects.create(name="Teknoloji")
        self.supplier = Supplier.objects.create(name="MSI")

    def test_base_viewset_sets_audit_fields_on_create(self):
        response = self.client.post(
            "/api/products/",
            {
                "name": "MSI Laptop",
                "sku": "MSI-001",
                "category": self.category.id,
                "supplier": self.supplier.id,
                "price": "45000.00",
                "stock": 5,
                "low_stock_threshold": 2,
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        product = Product.objects.get(id=response.data["id"])
        self.assertEqual(product.created_by, self.admin_user)
        self.assertEqual(product.updated_by, self.admin_user)
        self.assertEqual(response.data["created_by_username"], "admin")

    def test_base_viewset_soft_deletes_and_restores_record(self):
        product = Product.objects.create(
            name="MSI Mouse",
            sku="MSI-MOUSE-001",
            category=self.category,
            supplier=self.supplier,
            price=1500,
            stock=8,
            low_stock_threshold=2,
        )

        delete_response = self.client.delete(f"/api/products/{product.id}/")

        self.assertEqual(delete_response.status_code, status.HTTP_204_NO_CONTENT)
        product.refresh_from_db()
        self.assertFalse(product.is_active)
        self.assertEqual(product.updated_by, self.admin_user)

        list_response = self.client.get("/api/products/")
        listed_ids = [item["id"] for item in list_response.data["results"]]
        self.assertNotIn(product.id, listed_ids)

        inactive_response = self.client.get("/api/products/?include_inactive=true")
        inactive_ids = [item["id"] for item in inactive_response.data["results"]]
        self.assertIn(product.id, inactive_ids)

        restore_response = self.client.post(f"/api/products/{product.id}/restore/")

        self.assertEqual(restore_response.status_code, status.HTTP_200_OK)
        product.refresh_from_db()
        self.assertTrue(product.is_active)


    def test_product_viewset_generates_next_product_code(self):
        Product.objects.create(
            name="MSI Keyboard",
            sku="PRD-0001",
            category=self.category,
            supplier=self.supplier,
            price=1200,
            stock=3,
            low_stock_threshold=1,
        )

        response = self.client.get("/api/products/generate-code/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["code"], "PRD-0002")
