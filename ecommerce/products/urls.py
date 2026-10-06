from rest_framework.routers import DefaultRouter
from django.urls import path, include

from products.views import SubCategoryView,CategoryView,ProductView,ProductVariantView,ProductImageView




urlpatterns =[
    path('categories/',CategoryView.as_view(),name='all_categories'),
    path('categories/<int:category_id>/',CategoryView.as_view(),name='category'),

]