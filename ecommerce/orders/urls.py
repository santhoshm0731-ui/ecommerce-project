from rest_framework.routers import DefaultRouter
from django.urls import path, include
from .views import OrderView,OrderItemView,CheckoutView,OrderCancelView,AdminOrderView

router=DefaultRouter()

router.register(
    "items",
    OrderItemView,
    "order-items"
)
router.register("admin",
          AdminOrderView,
          basename="status-change"
)

router.register(
    "",
    OrderView,
    basename="user-orders"
)


urlpatterns=[
    path('checkout/',CheckoutView.as_view(),name='cart-checkout'),
    path('cancel/',OrderCancelView.as_view(),name='order-cancel'),
    path("",include(router.urls))
]