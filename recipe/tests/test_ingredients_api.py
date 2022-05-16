from django.urls import reverse
from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APIClient

from recipe.models import Ingredient
from recipe.serializers import IngredientSerializer

INGREDIENTS_URL = reverse("recipe:ingredient-list")


class PublicIngredientApiTests(TestCase):
    """Test publicly available Ingredient APIs"""

    def setUp(self):
        self.client = APIClient()

    def test_login_required(self):
        """Test that login required to retrive ingredients"""
        res = self.client.get(INGREDIENTS_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateIngredientApiTests(TestCase):
    """Test authorized ingredient APIs"""

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            "example@email.com", "testpass"
        )
        self.client.force_authenticate(self.user)

    def test_retrive_ingredients(self):
        """Test retriving ingredients"""
        Ingredient.objects.create(user=self.user, name="ingredient1")
        Ingredient.objects.create(user=self.user, name="ingredient2")

        res = self.client.get(INGREDIENTS_URL)
        ingredients = Ingredient.objects.all()
        serializer = IngredientSerializer(ingredients, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_ingredients_limited_to_user(self):
        """Test that ingredients are limited to a user"""
        user2 = get_user_model().objects.create_user("example2@email.com", "passtest")
        Ingredient.objects.create(user=user2, name="ingredient1")
        ingredient = Ingredient.objects.create(user=self.user, name="ingredient2")

        res = self.client.get(INGREDIENTS_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]["name"], ingredient.name)

    def test_creating_ingredient_successful(self):
        """Test that creating a new ingredient is successful"""
        payload = {"name": "ingreditn1"}
        res = self.client.post(INGREDIENTS_URL, payload)

        is_ingredient_exists = Ingredient.objects.filter(
            user=self.user, name=payload["name"]
        ).exists()

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertTrue(is_ingredient_exists)

    def test_creating_ingredient_invalid(self):
        """Test that creating a new ingredient with invalid payload fails"""
        payload = {"name": ""}
        res = self.client.post(INGREDIENTS_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
