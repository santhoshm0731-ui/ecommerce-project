from django.contrib import admin
from .models import Order, OrderItem


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("id", "order_number", "customer", "status", "payment_method", "total_amount", "created_at")
    list_filter = ("status", "payment_method", "created_at")
    search_fields = ("order_number", "customer__email")
    readonly_fields = ("order_number", "created_at")


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ("id", "order", "product_variant", "quantity", "unit_price", "subtotal")
