from django.contrib import admin
from django.contrib.auth import get_user_model
from .models import Address

User = get_user_model()


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ("id", "email", "is_staff", "is_active")
    list_filter = ("is_staff", "is_active")
    search_fields = ("email",)


@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = ("id", "customer", "city", "state", "zip_code", "country")
    list_filter = ("state", "country")
    search_fields = ("customer__email", "city", "zip_code")

