import json
from urllib import response

from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken
from accounts.models import Address,User # Adjust this import to match your actual app name

User = get_user_model()


class AddressAPITests(APITestCase):

    def setUp(self):
        # 1. We create two completely separate users for isolation testing
        self.user_a = User.objects.create_user(
            email="usera@test.com", phone="9999999991", password="password123"
        )
        self.user_b = User.objects.create_user(
            email="userb@test.com", phone="9999999992", password="password123"
        )

        # 2. Generate real JWT access tokens for both users
        self.token_a = str(RefreshToken.for_user(self.user_a).access_token)
        self.token_b = str(RefreshToken.for_user(self.user_b).access_token)

        # 3. Seed one baseline address belonging strictly to user_a
        self.address_a = Address.objects.create(
            customer=self.user_a,
            home_no="123",
            building_name="Alpha Towers",
            street="Main Street",
            nearby_landmark="Near Tech Park",
            zip_code="560001",
            type="home",
            city="Bengaluru",
            state="Karnataka",
            country="India",
            is_default=True
        )

        # Base API endpoints mapping your urls.py structure
        self.url_list_create = '/api/auth/addresses/'

    # =========================================================================
    # 🔒 AUTHENTICATION & PRIVACY ISOLATION TESTS
    # =========================================================================

    def test_anonymous_user_is_blocked(self):
        """Guests without tokens should get kicked out immediately."""
        self.client.credentials()  # Wipe out any login headers
        response = self.client.get(self.url_list_create)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_user_can_only_see_their_own_addresses(self):
        """User B should NOT see User A's addresses when listing."""
        # Log in as User B (who has 0 addresses seeded)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token_b}')
        response = self.client.get(self.url_list_create)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Check that the address list array returned is empty for User B
        self.assertEqual(len(response.data['address']), 0)

    def test_user_cannot_patch_someone_elses_address(self):
        """Privacy Barrier: User B shouldn't be able to edit User A's address ID."""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token_b}')
        url_detail = f'/api/auth/addresses/{self.address_a.id}/'
        payload = {'building_name': 'Hacked Towers'}

        response = self.client.patch(url_detail, payload, format='json')
        # Because your view uses user.addresses.get(), it drops a clean 404!
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_user_cannot_delete_someone_elses_address(self):
        """Privacy Barrier: User B shouldn't be able to delete User A's address."""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token_b}')
        url_detail = f'/api/auth/addresses/{self.address_a.id}/'

        response = self.client.delete(url_detail)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    # =========================================================================
    # ✉️ DATA & VALIDATION BOUNDARY TESTS
    # =========================================================================

    def test_create_address_success(self):
        """Submitting a complete valid payload adds a new address record."""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token_a}')
        payload = {
            "home_no": "456",
            "building_name": "Beta Vista",
            "street": "Cross Road",
            "nearby_landmark": "Opposite Mall",
            "zip_code": "560002",
            "type": "office",
            "city": "Bengaluru",
            "state": "Karnataka",
            "country": "India",
            "is_default": False
        }
        response = self.client.post(self.url_list_create, payload, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        # Verify it actually hit the database
        self.assertTrue(Address.objects.filter(home_no="456").exists())

    def test_create_address_fails_if_home_no_exceeds_max_length(self):
        """Data Boundary Check: home_no max_length=4. Sending 5 chars must fail."""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token_a}')
        payload = {
            "home_no": "12345",  # 🚨 5 characters! Exceeds the max limit
            "building_name": "Beta Vista",
            "street": "Cross Road",
            "nearby_landmark": "Opposite Mall",
            "zip_code": "560002",
            "type": "Office",
            "city": "Bengaluru",
            "state": "Karnataka",
            "country": "India"
        }
        response = self.client.post(self.url_list_create, payload, format='json')
        # The serializer should catch this validation fault
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('home_no', response.data['error'])

    def test_patch_address_success(self):
        """Updating your own address fields modifies the record cleanly."""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token_a}')
        url_detail = f'/api/auth/addresses/{self.address_a.id}/'
        payload = {'building_name': 'Omega Towers'}

        response = self.client.patch(url_detail, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Pull it fresh out of the DB to confirm the update stuck
        self.address_a.refresh_from_db()
        self.assertEqual(self.address_a.building_name, 'Omega Towers')


from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()


# Inherit directly from APITestCase
class UserAPITests(APITestCase):

    def setUp(self):
        # 1. We create two completely separate users for isolation testing
        self.user_a = User.objects.create_user(
            email="usera@test.com", phone="9999999991", password="password123"
        )
        self.user_b = User.objects.create_user(
            email="userb@test.com", phone="9999999992", password="password123"
        )
        self.user_admin = User.objects.create_superuser(
            email="admina@test.com", phone="9999999981", password="password123"
        )

        # 2. Generate tokens cleanly
        self.token_a = str(RefreshToken.for_user(self.user_a).access_token)
        self.token_b = str(RefreshToken.for_user(self.user_b).access_token)
        self.token_admin = str(RefreshToken.for_user(self.user_admin).access_token)

        self.token_a_refresh = str(RefreshToken.for_user(self.user_a))

    def test_user_account_create_success(self):
        url = '/api/auth/register/'  # Added leading slash
        payload = {'email': 'test1@gmail.com', 'phone': '8970998870', 'password': 'test1@123','first_name':'tester'}
        response = self.client.post(url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(User.objects.filter(email='test1@gmail.com').exists())

    def test_user_account_create_missing_field(self):
        url = '/api/auth/register/'
        payload = {'email': 'test2@gmail.com', 'password': 'test1@123'}  # missing phone
        response = self.client.post(url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_user_create_account_with_existing_mail(self):
        url = '/api/auth/register/'
        # Use 'usera@test.com' because it was already created in setUp()!
        payload = {'email': 'usera@test.com', 'phone': '8970998871', 'password': 'test1@123'}
        response = self.client.post(url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_user_create_account_with_existing_phone(self):
        url = '/api/auth/register/'
        # Use phone '9999999991' because user_a already owns it!
        payload = {'email': 'test2@gmail.com', 'phone': '9999999991', 'password': 'test1@123'}
        response = self.client.post(url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_user_login_success(self):
        url = '/api/auth/login/'
        payload = {'email': "usera@test.com", 'password': "password123"}
        response = self.client.post(url, payload, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Check that the tokens are present in the response
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)

    def test_user_login_with_missing_data(self):
        url = '/api/auth/login/'
        payload = {'password': "password123"}
        response = self.client.post(url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_user_login_invalid_data(self):
        url = '/api/auth/login/'
        # Changed password to a wrong one so it actually triggers a failure response
        payload = {'email': 'usera@test.com', 'password': "wrong_password"}
        response = self.client.post(url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_user_logout_success(self):
        url = '/api/auth/logout/'
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token_a}')
        payload = {'refresh': self.token_a_refresh}
        response = self.client.post(url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_user_profile_success(self):
        url = '/api/auth/me/'
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token_a}')
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['email'], 'usera@test.com')

    def test_user_cannot_get_profile_without_token(self):
        url = '/api/auth/me/'
        self.client.credentials()  # Anonymous user (no token)
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_admin_view_success_with_admin_token(self):
        url = '/api/auth/admin-test/'
        # Pass the admin token header for a GET request
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token_admin}')
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_admin_view_fails_for_normal_user(self):
        url = '/api/auth/admin-test/'
        # Pass a regular customer token to verify they are blocked
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token_a}')
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)







