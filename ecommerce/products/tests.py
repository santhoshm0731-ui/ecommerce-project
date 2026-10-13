import tempfile

from PIL import Image
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken
from products.models import Category, SubCategory, Product, ProductVariant, ProductImage

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
        response = self.client.get('/api/products/categories/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('categories', response.data)
        self.assertEqual(len(response.data['categories']), 2)

    def test_get_single_category_without_token_success(self):
        """NO TOKEN REQUIRED: Public guests can fetch a single category endpoint."""
        self.client.credentials()
        response = self.client.get(f'/api/products/categories/{self.cat_men.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['category']['name'], "Men's Wear")

    def test_customer_token_blocked_from_posting_category(self):
        """TOKEN RESTRICTED: A standard customer JWT cannot write a new category."""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.customer_token}')
        payload = {'name': 'Kids Wear', 'description': 'Children items'}
        response = self.client.post('/api/products/categories/', payload)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_admin_token_can_create_category(self):
        """TOKEN REQUIRED: An admin JWT token successfully publishes a category."""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.admin_token}')
        payload = {'name': 'Ethnic Wear', 'description': 'Traditional cloths', 'is_active': True}
        response = self.client.post('/api/products/categories/', payload)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Category.objects.filter(name='Ethnic Wear').exists())

    # =========================================================================
    # 🗂️ SUBCATEGORY TESTS (ModelViewSet - Uses 'AllowAny' for GET)
    # =========================================================================

    def test_get_subcategories_without_token_returns_only_active(self):
        """NO TOKEN REQUIRED: Guests view active subcategories."""
        self.client.credentials()
        response = self.client.get('/api/products/subcategories/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['name'], "Jeans")  # 📌 Ensure '[0]' index is included here!

    def test_get_subcategories_with_particular_category(self):
        """NO TOKEN REQUIRED: Guests view active subcategories."""
        self.client.credentials()
        response = self.client.get('/api/products/subcategories/1/')
        print(response)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(len(response.data), 1)


    def test_admin_token_bypasses_filters_to_see_all_subcategories(self):
        """TOKEN REQUIRED: Admin token sees the entire inventory (including draft subcategories)."""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.admin_token}')
        response = self.client.get('/api/products/subcategories/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Admin gets both active and inactive lines (Jeans + Jackets)
        self.assertEqual(len(response.data), 2)

    def test_customer_token_blocked_from_deleting_subcategory(self):
        """TOKEN RESTRICTED: Standard client tokens cannot perform a subcategory wipe."""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.customer_token}')
        response = self.client.delete(f'/api/products/subcategories/{self.sub_jeans.id}/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class ProductCatalogAPITests(APITestCase):

    def setUp(self):
        # 1. Accounts Setup
        self.customer = User.objects.create_user(
            email="shopper@test.com", phone="9999999991", password="password123"
        )
        self.admin = User.objects.create_superuser(
            email="admin@test.com", phone="9999999992", password="password123"
        )

        self.customer_token = str(RefreshToken.for_user(self.customer).access_token)
        self.admin_token = str(RefreshToken.for_user(self.admin).access_token)

        # 2. Category & SubCategory Seeding
        self.category = Category.objects.create(name="Apparel", is_active=True)
        self.subcategory = SubCategory.objects.create(
            category=self.category, name="Shoes", description="Footwear Collection", is_active=True
        )

        # 3. Product Inventory Seeding (Linked to subcategory)
        self.active_product = Product.objects.create(
            subcategory=self.subcategory, name="Running Shoes", description="Comfortable sneakers", is_active=True
        )
        self.inactive_product = Product.objects.create(
            subcategory=self.subcategory, name="Secret Hoodie", description="Unreleased item", is_active=False
        )

        # 4. Product Variants Seeding (Matching exact fields: size, color, price, stock, sku)
        self.variant_active = ProductVariant.objects.create(
            product=self.active_product, size="M", color="Red", price=1200.00, stock=50, sku="SHOE-M-RED",
            is_active=True
        )
        self.variant_hidden = ProductVariant.objects.create(
            product=self.active_product, size="L", color="Blue", price=1300.00, stock=20, sku="SHOE-L-BLU",
            is_active=False
        )
        self.variant_of_inactive_product = ProductVariant.objects.create(
            product=self.inactive_product, size="XL", color="Black", price=2500.00, stock=10, sku="HD-XL-BLK",
            is_active=True
        )

        # 5. Product Images Seeding (Including required alt_text field)
        self.image_of_active_product = ProductImage.objects.create(
            product=self.active_product, image="products/shoes.jpg", alt_text="Shoes Main View"
        )
        self.image_of_inactive_product = ProductImage.objects.create(
            product=self.inactive_product, image="products/hidden_hoodie.jpg", alt_text="Hoodie Draft View"
        )

        # Endpoint mappings matching your router configuration
        self.url_products = '/api/products/products/'
        self.url_variants = '/api/products/variants/'
        self.url_images = '/api/products/images/'

    # =========================================================================
    # 📦 PRODUCT VIEWSET TESTS
    # =========================================================================

    def test_guest_views_only_active_products(self):
        """Public visitors view active items; hidden products are filtered out."""
        self.client.credentials()
        response = self.client.get(self.url_products)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['name'], "Running Shoes")

    def test_admin_bypasses_filters_to_see_all_products(self):
        """Admin accounts see the complete inventory rows."""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.admin_token}')
        response = self.client.get(self.url_products)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_customer_blocked_from_creating_product(self):
        """Standard shoppers cannot create a new product entry."""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.customer_token}')
        payload = {'subcategory': self.subcategory.id, 'name': 'T-Shirt', 'description': 'Cotton tee',
                   'is_active': True}
        response = self.client.post(self.url_products, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    # =========================================================================
    # 🗂️ PRODUCT VARIANT VIEWSET TESTS
    # =========================================================================

    def test_guest_views_filtered_variants(self):
        """Guests only see active variants belonging to active products."""
        self.client.credentials()
        response = self.client.get(self.url_variants)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['sku'], "SHOE-M-RED")

    def test_admin_sees_all_variants(self):
        """Admin accounts bypass filtering to see every variant entry."""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.admin_token}')
        response = self.client.get(self.url_variants)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 3)

    # =========================================================================
    # 📷 PRODUCT IMAGE VIEWSET TESTS
    # =========================================================================

    def test_guest_cannot_see_images_of_inactive_products(self):
        """Images tied to hidden products are hidden from guests."""
        self.client.credentials()
        response = self.client.get(self.url_images)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_admin_can_upload_product_image(self):
        """Admin can successfully upload an image binary via multipart form-data."""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.admin_token}')

        image = Image.new('RGB', (100, 100), color='red')
        with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as tmp:
            image.save(tmp, format='JPEG')
            tmp.seek(0)
            mock_image = SimpleUploadedFile("test_shoe.jpg", tmp.read(), content_type="image/jpeg")

        payload = {
            'product': self.active_product.id,
            'image': mock_image,
            'alt_text': 'Side angle view'
        }

        response = self.client.post(self.url_images, payload, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
class ProductAPITests(APITestCase):

    def setUp(self):
        # Users
        self.customer = User.objects.create_user(
            email="customer@test.com",
            phone="9999999991",
            password="password123"
        )

        self.admin = User.objects.create_superuser(
            email="admin@test.com",
            phone="9999999992",
            password="password123"
        )

        # JWT tokens
        self.customer_token = str(
            RefreshToken.for_user(self.customer).access_token
        )

        self.admin_token = str(
            RefreshToken.for_user(self.admin).access_token
        )

        # Category
        self.category = Category.objects.create(
            name="Men's Wear",
            description="Men clothing",
            is_active=True
        )

        # Subcategories
        self.jeans = SubCategory.objects.create(
            category=self.category,
            name="Jeans",
            description="Denim collection",
            is_active=True
        )

        self.shirts = SubCategory.objects.create(
            category=self.category,
            name="Shirts",
            description="Shirt collection",
            is_active=True
        )

        # Products
        self.blue_jeans = Product.objects.create(
            subcategory=self.jeans,
            name="Blue Jeans",
            description="Classic blue denim jeans",
            is_active=True
        )

        self.black_jeans = Product.objects.create(
            subcategory=self.jeans,
            name="Black Jeans",
            description="Black denim jeans",
            is_active=True
        )

        self.red_shirt = Product.objects.create(
            subcategory=self.shirts,
            name="Red Shirt",
            description="Cotton red shirt",
            is_active=True
        )

        self.draft_jeans = Product.objects.create(
            subcategory=self.jeans,
            name="Draft Jeans",
            description="Draft product",
            is_active=False
        )

    # ============================================================
    # BASIC GET TESTS
    # ============================================================

    def test_guest_can_get_products(self):
        self.client.credentials()

        response = self.client.get(
            "/api/products/products/"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

    def test_guest_sees_only_active_products(self):
        self.client.credentials()

        response = self.client.get(
            "/api/products/products/"
        )

        product_names = [
            product["name"]
            for product in response.data
        ]

        self.assertIn("Blue Jeans", product_names)
        self.assertIn("Black Jeans", product_names)
        self.assertIn("Red Shirt", product_names)
        self.assertNotIn("Draft Jeans", product_names)

    def test_admin_sees_active_and_inactive_products(self):
        self.client.credentials(
            HTTP_AUTHORIZATION=f"Bearer {self.admin_token}"
        )

        response = self.client.get(
            "/api/products/products/"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

        product_names = [
            product["name"]
            for product in response.data
        ]

        self.assertIn("Blue Jeans", product_names)
        self.assertIn("Draft Jeans", product_names)

    # ============================================================
    # PERMISSION TESTS
    # ============================================================

    def test_customer_cannot_create_product(self):
        self.client.credentials(
            HTTP_AUTHORIZATION=f"Bearer {self.customer_token}"
        )

        payload = {
            "name": "New Product",
            "description": "New product",
            "subcategory": self.jeans.id,
            "is_active": True
        }

        response = self.client.post(
            "/api/products/products/",
            payload
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN
        )

    def test_admin_can_create_product(self):
        self.client.credentials(
            HTTP_AUTHORIZATION=f"Bearer {self.admin_token}"
        )

        payload = {
            "name": "White Shirt",
            "description": "Cotton white shirt",
            "subcategory": self.shirts.id,
            "is_active": True
        }

        response = self.client.post(
            "/api/products/products/",
            payload
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED
        )

        self.assertTrue(
            Product.objects.filter(
                name="White Shirt"
            ).exists()
        )

    def test_customer_cannot_update_product(self):
        self.client.credentials(
            HTTP_AUTHORIZATION=f"Bearer {self.customer_token}"
        )

        response = self.client.patch(
            f"/api/products/products/{self.blue_jeans.id}/",
            {
                "name": "Updated Jeans"
            }
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN
        )

    def test_customer_cannot_delete_product(self):
        self.client.credentials(
            HTTP_AUTHORIZATION=f"Bearer {self.customer_token}"
        )

        response = self.client.delete(
            f"/api/products/products/{self.blue_jeans.id}/"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN
        )

    # ============================================================
    # SUBCATEGORY FILTER
    # ============================================================

    def test_guest_can_filter_products_by_subcategory(self):
        self.client.credentials()

        response = self.client.get(
            f"/api/products/products/?subcategory={self.jeans.id}"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

        product_names = [
            product["name"]
            for product in response.data
        ]

        self.assertIn("Blue Jeans", product_names)
        self.assertIn("Black Jeans", product_names)
        self.assertNotIn("Red Shirt", product_names)
        self.assertNotIn("Draft Jeans", product_names)

    # ============================================================
    # SEARCH
    # ============================================================

    def test_search_by_product_name(self):
        self.client.credentials()

        response = self.client.get(
            "/api/products/products/?search=Jeans"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

        product_names = [
            product["name"]
            for product in response.data
        ]

        self.assertIn("Blue Jeans", product_names)
        self.assertIn("Black Jeans", product_names)
        self.assertNotIn("Red Shirt", product_names)
        self.assertNotIn("Draft Jeans", product_names)

    def test_search_by_description(self):
        self.client.credentials()

        response = self.client.get(
            "/api/products/products/?search=Cotton"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

        product_names = [
            product["name"]
            for product in response.data
        ]

        self.assertIn("Red Shirt", product_names)

    def test_search_with_no_results(self):
        self.client.credentials()

        response = self.client.get(
            "/api/products/products/?search=Shoes"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

        self.assertEqual(
            len(response.data),
            0
        )

    # ============================================================
    # ORDERING
    # ============================================================

    def test_ordering_by_name(self):
        self.client.credentials()

        response = self.client.get(
            "/api/products/products/?ordering=name"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

        names = [
            product["name"]
            for product in response.data
        ]

        self.assertEqual(
            names,
            sorted(names)
        )

    def test_ordering_by_newest(self):
        self.client.credentials()

        response = self.client.get(
            "/api/products/products/?ordering=-created_at"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

    # ============================================================
    # COMBINED FILTER + SEARCH + ORDERING
    # ============================================================

    def test_subcategory_search_and_ordering_together(self):
        self.client.credentials()

        response = self.client.get(
            f"/api/products/products/"
            f"?subcategory={self.jeans.id}"
            f"&search=Jeans"
            f"&ordering=name"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

        product_names = [
            product["name"]
            for product in response.data
        ]

        self.assertEqual(
            product_names,
            ["Black Jeans", "Blue Jeans"]
        )