from django.db import models
from django.utils import timezone
from orders.models import Order
from django.conf import settings

status=[
    ("PENDING","pending"),
    ("PROCESSING","processing"),
    ("SUCCESS","success"),
    ("FAILED","failed"),
    ("REFUNDED", "refunded"),
    ("REFUND_INITIATED","refund_initiated")
]

class Payment(models.Model):
    customer=models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="payments",
        on_delete=models.PROTECT
    )
    order=models.ForeignKey(
        Order,
        related_name="payments",
        on_delete=models.PROTECT
    )
    razorpay_order_id=models.CharField(
        max_length=100,
        unique=True,
        blank=False
    )
    razorpay_payment_id=models.CharField(
        max_length=300,
        unique=True,
        null=True,
        blank=True
    )
    razorpay_signature=models.CharField(
        max_length=100,
        null=True,
        blank=True
    )
    amount=models.DecimalField(max_digits=12, decimal_places=2)
    status=models.CharField(default="PENDING",choices=status,max_length=20)
    created_at=models.DateTimeField(default=timezone.now)

