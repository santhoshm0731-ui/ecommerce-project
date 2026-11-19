from rest_framework.routers import DefaultRouter
from django.urls import path, include
from .views import OrderView,OrderItemView,CheckoutView

router=DefaultRouter()

router.register(
    "items",
    OrderItemView,
    "order-items"
)

router.register(
    "",
    OrderView,
    basename="user-orders"
)


urlpatterns=[
    path('checkout/',CheckoutView.as_view(),name='cart-checkout'),
    path("",include(router.urls))
]