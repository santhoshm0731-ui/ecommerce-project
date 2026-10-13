from rest_framework.routers import DefaultRouter
from django.urls import path, include

from products.views import SubCategoryView,CategoryView,ProductView,ProductVariantView,ProductImageView

router = DefaultRouter()
router.register(
    "subcategories",
    SubCategoryView,
    basename="subcategory"
)

router.register(
    "products",
    ProductView,
    basename="product"
)

router.register(
    "variants",
    ProductVariantView,
    basename="variant"
)

router.register(
    "images",
    ProductImageView,
    basename="product-image"
)

urlpatterns =[
    path('categories/',CategoryView.as_view(),name='all_categories'),
    path('categories/<int:category_id>/',CategoryView.as_view(),name='category'),
    path('', include(router.urls)),
]