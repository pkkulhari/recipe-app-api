from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status

CREATE_USER_URL = reverse("accounts:create")
CREATE_TOKEN_URL = reverse("accounts:token")
ME_URL = reverse("accounts:me")


def create_user(**kwargs):
    return get_user_model().objects.create_user(**kwargs)


class PublicUserApiTests(TestCase):
    """Test the user APIs (Public)"""

    def setUp(self):
        self.client = APIClient()

    def test_create_valid_user_success(self):
        """Test creating a user with valid payload is successfull"""
        payload = {
            "email": "example@email.com",
            "password": "password123",
            "name": "Test Name",
        }

        res = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        user = get_user_model().objects.get(**res.data)
        self.assertTrue(user.check_password(payload["password"]))
        self.assertNotIn("password", res.data)

    def test_user_exists(self):
        """Test create a user that already exists fails"""
        payload = {"email": "example@email.com", "password": "password123"}

        res = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        user_exists = get_user_model().objects.filter(email=payload["email"]).exists()
        self.assertFalse(user_exists)

    def test_password_too_short(self):
        """Test that password must be at least 5 characters long"""
        payload = {"email": "example@email.com", "password": "pw"}
        res = self.client.post(CREATE_USER_URL, payload)
        user_exists = get_user_model().objects.filter(email=payload["email"]).exists()

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(user_exists)

    def test_create_user_token(self):
        """Test that user token creation is successfull"""
        payload = {"email": "example@email.com", "password": "password123"}
        create_user(**payload)
        res = self.client.post(CREATE_TOKEN_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn("token", res.data)

    def test_create_user_token_invalid_credentials(self):
        """Test that creating user token with invalid credentials fails"""
        create_user(email="example@email.com", password="password123")
        payload = {"email": "example@email.com", "password": "wrongpass"}
        res = self.client.post(CREATE_TOKEN_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertNotIn("token", res.data)

    def test_create_token_with_no_user(self):
        payload = {"email": "example@email.com", "password": "password123"}
        res = self.client.post(CREATE_TOKEN_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertNotIn("token", res.data)

    def test_retrieve_user_unauthorized(self):
        """Test the authentication is required to retrieve user's info"""
        res = self.client.get(ME_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateUserApiTests(TestCase):
    """Tests for private user APIs that require authentication"""

    def setUp(self):
        self.user = create_user(email="example@email.com", password="testpass")
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def test_retrieve_user_profile_success(self):
        """Test that retrieving user's profile is successful"""
        res = self.client.get(ME_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, {"email": self.user.email, "name": ""})

    def test_user_retrieve_post_method_not_allowed(self):
        """Test that the POST method not allowed for me url"""
        res = self.client.post(ME_URL, {})

        self.assertEqual(res.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_user_profile_update_success(self):
        """Test that updating user profile is successful"""
        payload = {"name": "Test Name", "password": "newpass"}
        res = self.client.patch(ME_URL, payload)
        self.user.refresh_from_db()

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["name"], payload["name"])
        self.assertTrue(self.user.check_password(payload["password"]))
