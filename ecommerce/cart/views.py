from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import ValidationError

from .models import Cart, CartItem
from .serializers import CartSerializer, CartItemSerializer


class CartView(ModelViewSet):
    serializer_class = CartSerializer
    permission_classes = [IsAuthenticated]

    http_method_names = ["get", "post", "head", "options"]

    def get_queryset(self):
        return Cart.objects.filter(
            customer=self.request.user
        )

    def perform_create(self, serializer):
        user = self.request.user

        if Cart.objects.filter(customer=user).exists():
            raise ValidationError("Cart already exists.")

        serializer.save(customer=user)


class CartItemView(ModelViewSet):
    serializer_class = CartItemSerializer
    permission_classes = [IsAuthenticated]

    http_method_names = [
        "get",
        "post",
        "patch",
        "delete",
        "head",
        "options",
    ]

    def get_queryset(self):
        user = self.request.user

        return CartItem.objects.filter(
            cart__customer=user
        ).select_related("variant", "cart")

    def perform_create(self, serializer):
        user = self.request.user

        cart = Cart.objects.filter(customer=user).first()

        if cart is None:
            raise ValidationError(
                "Please create your cart before adding products."
            )
        variant = serializer.validated_data["variant"]
        requested_quantity = serializer.validated_data["quantity"]

        cart_item = CartItem.objects.filter(
            cart=cart,
            variant=variant
        ).first()

        if cart_item:
            new_quantity = cart_item.quantity + requested_quantity

            if new_quantity > variant.stock:
                raise ValidationError({
                    "quantity": "Requested quantity exceeds available stock."
                })

            cart_item.quantity = new_quantity
            cart_item.save(
                update_fields=["quantity", "updated_at"]
            )

            # Make the updated object available to the POST response.
            serializer.instance = cart_item

        else:
            if requested_quantity > variant.stock:
                raise ValidationError({
                    "quantity": "Requested quantity exceeds available stock."
                })

            serializer.save(cart=cart)