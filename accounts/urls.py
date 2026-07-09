from django.urls import path
from rest_framework.routers import DefaultRouter

from accounts.views import LoginView, LogoutView, ManagedUserViewSet, MeView

router = DefaultRouter()
router.register("users", ManagedUserViewSet, basename="managed-user")

urlpatterns = [
    path("login/", LoginView.as_view(), name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("me/", MeView.as_view(), name="me"),
] + router.urls
