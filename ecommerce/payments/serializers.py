from orders.models import Order
from . models import Payment
from rest_framework.exceptions import ValidationError
from rest_framework import serializers


class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model=Payment
        fields=[
            'id','customer','order','razorpay_order_id','razorpay_payment_id',
            'razorpay_signature','amount','status','created_at'
        ]

        read_only_fields=[
            'customer','razorpay_order_id','razorpay_payment_id','razorpay_signature',
            'amount','status','created_at'
        ]

class CreatePaymentSerializer(serializers.Serializer):
    order_id = serializers.IntegerField(required=True)
    def validate_order_id(self,value):
        if not self.context['request'].user.orders.filter(id=value).exists():
            raise ValidationError("Please select a valid order")
        order=self.context['request'].user.orders.filter(id=value).first()
        if order.status!="PENDING":
            raise ValidationError("Invalid order choice")
        return value

class VerifyPaymentSerializer(serializers.Serializer):
    razorpay_order_id=serializers.CharField(required=True,max_length=100)
    razorpay_payment_id=serializers.CharField(required=True,max_length=100)
    razorpay_signature=serializers.CharField(required=True,max_length=300)




