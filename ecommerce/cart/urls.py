from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import CartView, CartItemView


router = DefaultRouter()

router.register(
    "items",
    CartItemView,
    basename="cart-items"
)

router.register(
    "",
    CartView,
    basename="user-cart"
)

urlpatterns = [
    path("", include(router.urls))
]