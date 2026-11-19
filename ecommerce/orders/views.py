from decimal import Decimal
import uuid
from rest_framework.response import Response
from rest_framework.status import HTTP_201_CREATED

from products.models import ProductVariant
from .models import Order,OrderItem
from .serializers import OrderSerializer,OrderItemSerializer,CheckoutSerializer
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated
from cart.models import Cart,CartItem
from rest_framework.exceptions import ValidationError
from rest_framework.views import APIView
from django.db import transaction

class OrderView(ModelViewSet):
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ["get","head", "options"]

    def get_queryset(self):
        user=self.request.user
        return (
            Order.objects.filter(customer=user)
        )

class OrderItemView(ModelViewSet):
    serializer_class = OrderItemSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ["get","head", "options"]

    def get_queryset(self):
        user=self.request.user
        return (
            OrderItem.objects.filter(order__customer=user)
        ).select_related("order", "product_variant")

class CheckoutView(APIView):
    permission_classes = [IsAuthenticated]
    http_method_names = ['post','head','options']

    def post(self,request):
        total_amount=Decimal("0.00")
        user=self.request.user
        checkout_serializer = CheckoutSerializer(
            data=request.data,
            context={"request": request}
        )
        checkout_serializer.is_valid(raise_exception=True)
        address_id = checkout_serializer.validated_data["address_id"]

        with transaction.atomic():
            cart = Cart.objects.filter(customer=user).first()
            if cart is None:
                raise ValidationError('Cart not found')
            cart_items=list(CartItem.objects.filter(cart=cart).select_related("variant","variant__product"))
            if not cart_items:
                 raise ValidationError('Cart is empty')
            variant_ids = [item.variant.id for item in cart_items]
            locked_variants = ProductVariant.objects.select_for_update().in_bulk(variant_ids)

            for item in cart_items:
                variant = locked_variants[item.variant.id]
                if not variant.is_active:
                    raise ValidationError('the selected product is not active')
                if not variant.product.is_active:
                    raise ValidationError('the selected product is not active')
                if item.quantity > variant.stock:
                    raise ValidationError("Requested quantity exceeds available stock.")
                subtotal= variant.price*item.quantity
                total_amount+=subtotal

            address = user.addresses.get(id=address_id)
            shipping_address = (
                f"{address.home_no}, {address.building_name}, "
                f"{address.street}, {address.nearby_landmark}, "
                f"{address.city}, {address.state}, "
                f"{address.country} - {address.zip_code}"
            )

            order_number = uuid.uuid4().hex[:12].upper()

            order=Order.objects.create(
                customer=user,
                order_number=order_number,
                total_amount=total_amount,
                shipping_address=shipping_address
            )
            for item in cart_items:
                variant = locked_variants[item.variant.id]
                product_variant=variant
                quantity=item.quantity
                unit_price=variant.price
                subtotal=variant.price*quantity
                OrderItem.objects.create(
                    order=order,
                    product_variant= product_variant,
                    quantity=quantity,
                    unit_price=unit_price,
                    subtotal=subtotal
                )
                variant.stock -= item.quantity
                variant.save(update_fields=["stock"])
            CartItem.objects.filter(cart=cart).delete()
        return Response(
            {
                "message": "Order created successfully.",
                "order_id": order.id,
                "order_number": order.order_number,
                "total_amount": order.total_amount
            },
            status=HTTP_201_CREATED
        )







