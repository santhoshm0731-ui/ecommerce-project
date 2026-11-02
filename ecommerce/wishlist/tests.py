
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken

from accounts.models import User
from products.models import Category, SubCategory, Product
from wishlist.models import Wishlist


class WishlistAPITestCase(APITestCase):

    def setUp(self):
        # Create two customers
        self.user1 = User.objects.create_user(
            email="customer1@example.com",
            phone="9876543210",
            password="Testpass123!"
        )

        self.user2 = User.objects.create_user(
            email="customer2@example.com",
            phone="9876543211",
            password="Testpass123!"
        )

        # Authenticate customer 1
        refresh = RefreshToken.for_user(self.user1)
        self.client.credentials(
            HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}"
        )

        # Create product hierarchy
        self.category = Category.objects.create(
            name="Electronics",
            description="Electronic products",
            is_active=True
        )

        self.subcategory = SubCategory.objects.create(
            category=self.category,
            name="Mobiles",
            description="Mobile phones",
            is_active=True
        )

        self.product = Product.objects.create(
            subcategory=self.subcategory,
            name="Test Mobile",
            description="Test mobile description",
            is_active=True
        )

        self.wishlist_url = reverse("wishlist-list")

    # 1. Test adding a product to wishlist
    def test_add_product_to_wishlist(self):
        response = self.client.post(
            self.wishlist_url,
            {"product": self.product.id}
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(
            Wishlist.objects.filter(
                customer=self.user1,
                product=self.product
            ).exists()
        )

    # 2. Test retrieving wishlist
    def test_get_wishlist(self):
        Wishlist.objects.create(
            customer=self.user1,
            product=self.product
        )

        response = self.client.get(self.wishlist_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    # 3. Test duplicate product prevention
    def test_duplicate_product_in_wishlist(self):
        Wishlist.objects.create(
            customer=self.user1,
            product=self.product
        )

        response = self.client.post(
            self.wishlist_url,
            {"product": self.product.id}
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST
        )

    # 4. Test deleting wishlist item
    def test_delete_wishlist_item(self):
        wishlist_item = Wishlist.objects.create(
            customer=self.user1,
            product=self.product
        )

        response = self.client.delete(
            reverse("wishlist-detail", args=[wishlist_item.id])
        )

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(
            Wishlist.objects.filter(id=wishlist_item.id).exists()
        )

    # 5. Test customer cannot see another customer's wishlist
    def test_customer_cannot_see_other_customer_wishlist(self):
        Wishlist.objects.create(
            customer=self.user2,
            product=self.product
        )

        response = self.client.get(self.wishlist_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)

    # 6. Test customer cannot delete another customer's wishlist item
    def test_customer_cannot_delete_other_customer_wishlist(self):
        wishlist_item = Wishlist.objects.create(
            customer=self.user2,
            product=self.product
        )

        response = self.client.delete(
            reverse("wishlist-detail", args=[wishlist_item.id])
        )

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        self.assertTrue(
            Wishlist.objects.filter(id=wishlist_item.id).exists()
        )

    # 7. Test unauthenticated customer cannot access wishlist
    def test_unauthenticated_user_cannot_access_wishlist(self):
        self.client.credentials()

        response = self.client.get(self.wishlist_url)

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED
        )

    # 8. Test adding an invalid product ID
    def test_add_invalid_product_to_wishlist(self):
        response = self.client.post(
            self.wishlist_url,
            {"product": 999999}
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST
        )
