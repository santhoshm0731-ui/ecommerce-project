from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken
from products.models import Category, SubCategory

User = get_user_model()


class CategoryAndSubCategoryAPITests(APITestCase):

    def setUp(self):
        # 1. Setup Test Accounts & Generate Real JWT Access Tokens
        self.customer = User.objects.create_user(
            email="shopper@test.com", phone="9999999991", password="password123"
        )
        self.admin = User.objects.create_superuser(
            email="admin@test.com", phone="9999999992", password="password123"
        )

        self.customer_token = str(RefreshToken.for_user(self.customer).access_token)
        self.admin_token = str(RefreshToken.for_user(self.admin).access_token)

        # 2. Seed Apparel Test Data
        self.cat_men = Category.objects.create(
            name="Men's Wear", description="Apparel for men", is_active=True
        )
        self.cat_women = Category.objects.create(
            name="Women's Wear", description="Apparel for women", is_active=False  # Hidden draft category
        )

        self.sub_jeans = SubCategory.objects.create(
            category=self.cat_men, name="Jeans", description="Denim collection", is_active=True
        )
        self.sub_jackets = SubCategory.objects.create(
            category=self.cat_men, name="Jackets", description="Winter collection", is_active=False
        )

    # =========================================================================
    # 🏷️ CATEGORY TESTS (APIView - Uses 'AllowAny' for GET)
    # =========================================================================

    def test_get_categories_without_token_success(self):
        """NO TOKEN REQUIRED: Public guests can view all categories cleanly."""
        self.client.credentials()  # Simulates an anonymous visitor with no headers
        response = self.client.get('/api/auth/categories/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('categories', response.data)
        self.assertEqual(len(response.data['categories']), 2)

    def test_get_single_category_without_token_success(self):
        """NO TOKEN REQUIRED: Public guests can fetch a single category endpoint."""
        self.client.credentials()
        response = self.client.get(f'/api/auth/categories/{self.cat_men.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['category']['name'], "Men's Wear")

    def test_customer_token_blocked_from_posting_category(self):
        """TOKEN RESTRICTED: A standard customer JWT cannot write a new category."""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.customer_token}')
        payload = {'name': 'Kids Wear', 'description': 'Children items'}
        response = self.client.post('/api/auth/categories/', payload)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_admin_token_can_create_category(self):
        """TOKEN REQUIRED: An admin JWT token successfully publishes a category."""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.admin_token}')
        payload = {'name': 'Ethnic Wear', 'description': 'Traditional cloths', 'is_active': True}
        response = self.client.post('/api/auth/categories/', payload)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Category.objects.filter(name='Ethnic Wear').exists())

    # =========================================================================
    # 🗂️ SUBCATEGORY TESTS (ModelViewSet - Uses 'AllowAny' for GET)
    # =========================================================================

    def test_get_subcategories_without_token_returns_only_active(self):
        """NO TOKEN REQUIRED: Guests view active subcategories."""
        self.client.credentials()
        response = self.client.get('/api/auth/subcategories/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['name'], "Jeans")  # 📌 Ensure '[0]' index is included here!

    def test_admin_token_bypasses_filters_to_see_all_subcategories(self):
        """TOKEN REQUIRED: Admin token sees the entire inventory (including draft subcategories)."""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.admin_token}')
        response = self.client.get('/api/auth/subcategories/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Admin gets both active and inactive lines (Jeans + Jackets)
        self.assertEqual(len(response.data), 2)

    def test_customer_token_blocked_from_deleting_subcategory(self):
        """TOKEN RESTRICTED: Standard client tokens cannot perform a subcategory wipe."""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.customer_token}')
        response = self.client.delete(f'/api/auth/subcategories/{self.sub_jeans.id}/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)





