from django.db import models
from django.utils import timezone


class Category(models.Model):
    name = models.CharField(max_length=100, blank=False)
    description = models.TextField(max_length=200)
    is_active = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class SubCategory(models.Model):
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name="subcategories"
    )
    name = models.CharField(max_length=100, blank=False)
    description = models.TextField(max_length=200)
    is_active = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class Product(models.Model):
    subcategory = models.ForeignKey(
        SubCategory,
        on_delete=models.CASCADE,
        related_name="products"
    )
    name = models.CharField(max_length=100, blank=False)
    description = models.TextField(max_length=200)
    is_active = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class ProductImage(models.Model):
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="images"
    )
    image = models.ImageField(blank=False)
    alt_text = models.CharField(max_length=100)
    is_primary = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.alt_text


class ProductVariant(models.Model):
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="variants"
    )
    size = models.CharField(max_length=20, blank=False)
    color = models.CharField(max_length=20, blank=False)
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        blank=False
    )
    stock = models.PositiveIntegerField(blank=False)
    sku = models.CharField(max_length=10, unique=True)
    is_active = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["product", "size", "color"],
                name="unique_product_variant"
            )
        ]

    def __str__(self):
        return self.sku