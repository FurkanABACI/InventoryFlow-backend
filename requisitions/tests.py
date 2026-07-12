from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.test import APITestCase

from accounts.choices import UserRole
from accounts.models import UserProfile
from catalog.models import Category, Product, Supplier
from requisitions.choices import StockRequestStatus
from requisitions.models import StockRequest
from stock.choices import StockMovementType
from stock.models import StockMovement


class StockRequestFlowTests(APITestCase):
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

        self.category = Category.objects.create(name="Mutfak")
        self.supplier = Supplier.objects.create(name="Tabak Tedarik")

    def test_department_user_can_create_uncataloged_request(self):
        self.client.force_authenticate(self.department_user)

        response = self.client.post(
            "/api/stock-requests/",
            {
                "department": "Satinalma tarafindan degistirilmemeli",
                "requester_name": "Yemekhane Sorumlusu",
                "request_items": [
                    {
                        "requested_product_name": "Porselen tabak",
                        "requested_product_note": "Yemekhane icin",
                        "quantity": 10,
                    }
                ],
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        stock_request = StockRequest.objects.get(id=response.data["id"])
        self.assertEqual(stock_request.department, "Yemekhane")
        self.assertEqual(stock_request.items.first().requested_product_name, "Porselen tabak")

    def test_department_user_cannot_fulfill_request(self):
        stock_request = StockRequest.objects.create(
            requester_user=self.department_user,
            department="Yemekhane",
            requester_name="Yemekhane Sorumlusu",
        )

        self.client.force_authenticate(self.department_user)
        response = self.client.post(f"/api/stock-requests/{stock_request.id}/fulfill/")

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_uncataloged_request_can_be_linked_and_fulfilled_after_stock_arrives(self):
        stock_request = StockRequest.objects.create(
            requester_user=self.department_user,
            department="Yemekhane",
            requester_name="Yemekhane Sorumlusu",
        )
        request_item = stock_request.items.create(
            requested_product_name="Porselen tabak",
            quantity=10,
        )
        product = Product.objects.create(
            name="Porselen tabak",
            sku="TABAK-001",
            category=self.category,
            supplier=self.supplier,
            price=50,
            stock=12,
            low_stock_threshold=5,
        )

        self.client.force_authenticate(self.admin_user)

        first_fulfill_response = self.client.post(
            f"/api/stock-requests/{stock_request.id}/fulfill/"
        )
        self.assertEqual(first_fulfill_response.status_code, status.HTTP_400_BAD_REQUEST)

        stock_request.refresh_from_db()
        self.assertEqual(stock_request.status, StockRequestStatus.PURCHASE_NEEDED)

        link_response = self.client.post(
            f"/api/stock-requests/{stock_request.id}/items/{request_item.id}/link-product/",
            {"product": product.id},
            format="json",
        )
        self.assertEqual(link_response.status_code, status.HTTP_200_OK)

        stock_request.refresh_from_db()
        self.assertEqual(stock_request.status, StockRequestStatus.PENDING)
        request_item.refresh_from_db()
        self.assertEqual(request_item.product_id, product.id)

        final_fulfill_response = self.client.post(
            f"/api/stock-requests/{stock_request.id}/fulfill/"
        )
        self.assertEqual(final_fulfill_response.status_code, status.HTTP_200_OK)

        product.refresh_from_db()
        request_item.refresh_from_db()
        stock_request.refresh_from_db()

        self.assertEqual(product.stock, 2)
        self.assertEqual(request_item.delivered_quantity, 10)
        self.assertEqual(stock_request.status, StockRequestStatus.FULFILLED)
        self.assertTrue(
            StockMovement.objects.filter(
                product=product,
                movement_type=StockMovementType.OUT,
                quantity=10,
                source_type="stock_request",
                source_id=stock_request.id,
            ).exists()
        )
