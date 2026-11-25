from django.urls import path,include
from rest_framework.routers import DefaultRouter
from .views import PaymentView,CreatePaymentView,RazorPayWebhookView,VerifyPaymentView

router=DefaultRouter()
router.register(
    "",
    PaymentView,
    basename="user-payments"
)

urlpatterns=[
    path('create/',CreatePaymentView.as_view(),name="create-payment"),
    path('webhook/',RazorPayWebhookView.as_view(),name="verify_signature"),
    path('verify/',VerifyPaymentView.as_view(),name='verfy-payment'),
    path("",include(router.urls))
]

