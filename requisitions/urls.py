from rest_framework.routers import DefaultRouter

from requisitions.views import StockRequestViewSet

router = DefaultRouter()
router.register("stock-requests", StockRequestViewSet, basename="stock-request")

urlpatterns = router.urls
