from decimal import Decimal

from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.test import APITestCase

from accounts.choices import UserRole
from accounts.models import UserProfile
from catalog.models import Category, Product, ProductSupplier, Supplier
from receiving.models import GoodsReceipt, GoodsReceiptItem
from stock.choices import StockMovementType
from stock.models import StockMovement


class GoodsReceiptFlowTests(APITestCase):
    def setUp(self):
        self.admin_user = User.objects.create_user(
            username="admin",
            password="testpass123",
            is_staff=True,
        )
        UserProfile.objects.create(user=self.admin_user, role=UserRole.ADMIN)

        self.department_user = User.objects.create_user(
            username="yemekhane",
            password="testpass123",
        )
        UserProfile.objects.create(
            user=self.department_user,
            role=UserRole.DEPARTMENT,
            department="Yemekhane",
        )

        self.category = Category.objects.create(name="Teknoloji")
        self.supplier = Supplier.objects.create(name="MSI")
        self.product = Product.objects.create(
            name="MSI Laptop",
            sku="MSI-LAP-001",
            category=self.category,
            supplier=self.supplier,
            price=45000,
            stock=5,
            low_stock_threshold=2,
        )

    def test_goods_receipt_increases_stock_and_creates_stock_movement(self):
        self.client.force_authenticate(self.admin_user)

        response = self.client.post(
            "/api/goods-receipts/",
            {
                "supplier": self.supplier.id,
                "document_no": "IRS-001",
                "note": "Laptop teslimati",
                "receipt_items": [
                    {
                        "product": self.product.id,
                        "quantity": 3,
                        "unit_cost": "30000.00",
                    }
                ],
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        self.product.refresh_from_db()
        self.assertEqual(self.product.stock, 8)

        receipt = GoodsReceipt.objects.get(id=response.data["id"])
        self.assertEqual(receipt.supplier, self.supplier)
        self.assertTrue(
            GoodsReceiptItem.objects.filter(
                receipt=receipt,
                product=self.product,
                quantity=3,
                unit_cost=Decimal("30000.00"),
            ).exists()
        )
        self.assertTrue(
            StockMovement.objects.filter(
                product=self.product,
                movement_type=StockMovementType.IN,
                quantity=3,
                unit_cost=Decimal("30000.00"),
                source_type="goods_receipt",
                source_id=receipt.id,
            ).exists()
        )

        supplier_link = ProductSupplier.objects.get(
            product=self.product,
            supplier=self.supplier,
        )
        self.assertEqual(supplier_link.unit_cost, Decimal("30000.00"))

    def test_department_user_cannot_create_goods_receipt(self):
        self.client.force_authenticate(self.department_user)

        response = self.client.post(
            "/api/goods-receipts/",
            {
                "supplier": self.supplier.id,
                "receipt_items": [
                    {
                        "product": self.product.id,
                        "quantity": 1,
                        "unit_cost": "30000.00",
                    }
                ],
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
