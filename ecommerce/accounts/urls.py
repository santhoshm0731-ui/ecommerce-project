from os import name

from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from .views import RegisterView,LoginView,Meview,LogoutView,AdminTestView,AddressView
urlpatterns=[
    path('register/',RegisterView.as_view(),name='register'),
    path('login/',LoginView.as_view(),name='login'),
    path('me/',Meview.as_view(),name='my_info'),
    path('refresh/',TokenRefreshView.as_view(),name="refresh_token"),
    path('logout/',LogoutView.as_view(),name='logout'),
    path('admin-test/', AdminTestView.as_view(), name='test'),
    path('addresses/', AddressView.as_view(), name='my-address'),
    path('addresses/<int:address_id>/', AddressView.as_view(), name='update_address'),

]
