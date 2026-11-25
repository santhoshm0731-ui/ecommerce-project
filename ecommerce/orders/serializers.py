from .models import Order, OrderItem
from rest_framework import serializers

class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = [
            "id",
            "customer",
            "order_number",
            "status",
            "total_amount",
            "shipping_address",
            "created_at",
            "payment_method"
        ]
        read_only_fields = [
            "id",
            "customer",
            "order_number",
            "status",
            "total_amount",
            "created_at",
            "payment_method"
        ]


class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = [
            "id",
            "order",
            "product_variant",
            "quantity",
            "unit_price",
            "subtotal",
        ]
        read_only_fields = [
            "id",
            "order",
            "unit_price",
            "subtotal",
        ]

    def validate_quantity(self, value):
        if value <= 0:
            raise serializers.ValidationError(
                "Product quantity must be greater than 0."
            )
        return value

    def validate(self, attrs):
        variant = attrs.get(
            "product_variant",
            self.instance.product_variant if self.instance else None
        )

        quantity = attrs.get(
            "quantity",
            self.instance.quantity if self.instance else 1
        )

        if variant is None:
            raise serializers.ValidationError({
                "product_variant": "A product variant is required."
            })

        if not variant.is_active:
            raise serializers.ValidationError(
                "The selected variant is currently unavailable."
            )

        if not variant.product.is_active:
            raise serializers.ValidationError(
                "The product is currently unavailable."
            )

        if quantity > variant.stock:
            raise serializers.ValidationError({
                "quantity": "Requested quantity exceeds available stock."
            })

        return attrs

class CheckoutSerializer(serializers.Serializer):
    address_id=serializers.IntegerField(required=True)
    payment_method=serializers.ChoiceField(choices=Order.types, required=True)
    def validate_address_id(self,value):
        if not self.context['request'].user.addresses.filter(id=value).exists():
            raise serializers.ValidationError("Invalid address")
        return value

class OrderCancelSerializer(serializers.Serializer):
    order_id=serializers.IntegerField(required=True)
    def validate_order_id(self,value):
        if not self.context['request'].user.orders.filter(id=value).exists():
            raise serializers.ValidationError('Invalid order id.')
        return value