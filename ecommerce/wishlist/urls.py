from rest_framework.routers import DefaultRouter
from django.urls import path,include

from .views import WishlistView
router=DefaultRouter()

router.register(
    "",
    WishlistView,
    basename="wishlist"
)



urlpatterns=[
    path('',include(router.urls))
]