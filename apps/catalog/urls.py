from rest_framework.routers import DefaultRouter

from apps.catalog.views import (
    CategoryViewSet,
    ProductSupplierViewSet,
    ProductViewSet,
    SupplierViewSet,
)

router = DefaultRouter()
router.register("categories", CategoryViewSet, basename="category")
router.register("suppliers", SupplierViewSet, basename="supplier")
router.register("products", ProductViewSet, basename="product")
router.register("product-suppliers", ProductSupplierViewSet, basename="product-supplier")

urlpatterns = router.urls
