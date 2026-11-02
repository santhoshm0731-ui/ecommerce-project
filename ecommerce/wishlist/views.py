from rest_framework.exceptions import ValidationError
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated
from .models import Wishlist
from .serializers import WishlistSerializer

class WishlistView(ModelViewSet):
    serializer_class = WishlistSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return Wishlist.objects.filter(customer=user).select_related("product")

    def perform_create(self, serializer):
        product = serializer.validated_data["product"]

        if Wishlist.objects.filter(
            customer=self.request.user,
            product=product
        ).exists():
            raise ValidationError({
                "product": "This product is already in your wishlist."
            })

        serializer.save(customer=self.request.user)
