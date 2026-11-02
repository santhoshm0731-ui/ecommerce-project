from rest_framework import serializers
from .models import Cart, CartItem


class CartSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cart
        fields = [
            "id",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "created_at",
            "updated_at",
        ]


class CartItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = CartItem
        fields = [
            "id",
            "variant",
            "quantity",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "created_at",
            "updated_at",
        ]

    def validate_quantity(self, value):
        if value <= 0:
            raise serializers.ValidationError(
                "Product quantity must be greater than 0."
            )

        return value

    def validate(self, attrs):
        variant = attrs.get(
            "variant",
            self.instance.variant if self.instance else None
        )
        quantity = attrs.get(
            "quantity",
            self.instance.quantity if self.instance else 1
        )
        if variant and quantity > variant.stock:
            raise serializers.ValidationError({
                "quantity": "Requested quantity exceeds available stock."
            })
        if variant and not variant.is_active:
            raise serializers.ValidationError({
                "variant": "This product variant is not available."
            })
        if variant and not variant.product.is_active:
            raise serializers.ValidationError({
                "variant": "This product is not available."
            })

        if (
            self.instance
            and "variant" in attrs
            and attrs["variant"] != self.instance.variant
        ):
            raise serializers.ValidationError({
                "variant": "You cannot change the variant of an existing cart item."
            })

        return attrs