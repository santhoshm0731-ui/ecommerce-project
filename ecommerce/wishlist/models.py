from django.db import models
from django.conf import settings


class Wishlist(models.Model):
    customer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="wishlist_entries"
    )

    product = models.ForeignKey(
        "products.Product",
        on_delete=models.CASCADE,
        related_name="wishlist_entries"
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["customer", "product"],
                name="unique_customer_wishlist_product"
            )
        ]

    def __str__(self):
        return f"{self.customer.email} - {self.product.name}"