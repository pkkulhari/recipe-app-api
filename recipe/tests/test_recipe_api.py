from django.urls import reverse
from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status

from recipe.models import Ingredient, Recipe, Tag
from recipe.serializers import RecipeSerializer, RecipeDetailSerializer

RECIPES_URL = reverse("recipe:recipe-list")


def detail_url(recipe_id):
    return reverse("recipe:recipe-detail", args=[recipe_id])


def sample_recipe(**params):
    default = {"title": "recipe1", "time_minutes": 5, "price": 20.00}
    default.update(params)

    return Recipe.objects.create(**default)


def sample_tag(user, name="tag1"):
    return Tag.objects.create(user=user, name=name)


def sample_ingredient(user, name="ingredient1"):
    return Ingredient.objects.create(user=user, name=name)


class UnauthenticatedRecipeApiTests(TestCase):
    """Tests for unauthenticated recipe APIs"""

    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        """Test that authentication is required to retrieve recipes"""
        res = self.client.get(RECIPES_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedRecipeApiTests(TestCase):
    """Test for authenticated recipe APIs"""

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            "example@email.com", "testpass"
        )
        self.client.force_authenticate(self.user)

    def test_retrieving_recipes(self):
        """Test that retrieving recipes is successful"""
        sample_recipe(user=self.user)

        res = self.client.get(RECIPES_URL)
        recipes = Recipe.objects.all()
        serializer = RecipeSerializer(recipes, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_recipes_limited_to_user(self):
        """Test that recipes are limited to user"""
        user2 = get_user_model().objects.create_user("example2@email.com", "testpass")
        sample_recipe(user=user2)
        recipe = sample_recipe(user=self.user)

        res = self.client.get(RECIPES_URL)
        recipes = Recipe.objects.filter(user=self.user)
        serializer = RecipeSerializer(recipes, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data, serializer.data)

    def test_view_recipe_detail(self):
        """Test viewing recipe details"""
        recipe = sample_recipe(user=self.user)
        tag = sample_tag(user=self.user)
        ingredient = sample_ingredient(user=self.user)
        recipe.tags.add(tag)
        recipe.ingredients.add(ingredient)

        res = self.client.get(detail_url(recipe.id))
        serializer = RecipeDetailSerializer(recipe)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_create_recipe(self):
        """Test creating a new recipe"""
        payload = {"title": "recipe1", "time_minutes": 5, "price": 84.00}
        res = self.client.post(RECIPES_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        recipe = Recipe.objects.get(id=res.data["id"])
        for key in payload.keys():
            self.assertEqual(payload[key], getattr(recipe, key))

    def test_create_recipe_with_tags(self):
        """Test creating a new recipe with tags"""
        tag1 = sample_tag(user=self.user)
        tag2 = sample_tag(user=self.user, name="tag2")
        payload = {
            "title": "recipe1",
            "time_minutes": 3,
            "price": 5.00,
            "tags": [tag1.id, tag2.id],
        }
        res = self.client.post(RECIPES_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        recipe = Recipe.objects.get(id=res.data["id"])
        tags = recipe.tags.all()
        self.assertEqual(tags.count(), 2)
        self.assertIn(tag1, tags)
        self.assertIn(tag2, tags)

    def test_create_recipe_with_ingredients(self):
        """Test creating new recipe with ingredients"""
        ingredient1 = sample_ingredient(user=self.user)
        ingredient2 = sample_ingredient(user=self.user, name="ingredient2")
        payload = {
            "title": "recipe1",
            "time_minutes": 6,
            "price": 44.42,
            "ingredients": [ingredient1.id, ingredient2.id],
        }
        res = self.client.post(RECIPES_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        recipe = Recipe.objects.get(id=res.data["id"])
        ingredients = recipe.ingredients.all()
        self.assertEqual(ingredients.count(), 2)
        self.assertIn(ingredient1, ingredients)
        self.assertIn(ingredient2, ingredients)

    def test_recipe_partial_update(self):
        """Test updating recipe with patch"""
        recipe = sample_recipe(user=self.user)
        tag = sample_tag(user=self.user)
        recipe.tags.add(tag)

        payload = {"title": "recipe2", "price": 33.32}
        res = self.client.patch(detail_url(recipe.id), payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        recipe.refresh_from_db()
        tags = recipe.tags.all()
        self.assertEqual(tags.count(), 1)
        self.assertEqual(recipe.title, payload["title"])
        self.assertEqual(float(recipe.price), payload["price"])

    def test_recipe_full_update(self):
        """Test updating recipe with PUT"""
        recipe = sample_recipe(user=self.user)
        tag = sample_tag(user=self.user)
        recipe.tags.add(tag)

        payload = {"title": "recipe2", "time_minutes": 3, "price": 32}
        res = self.client.put(detail_url(recipe.id), payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        recipe.refresh_from_db()
        tags = recipe.tags.all()
        self.assertEqual(tags.count(), 0)
        self.assertEqual(recipe.title, payload["title"])
        self.assertEqual(recipe.time_minutes, payload["time_minutes"])
        self.assertEqual(recipe.price, payload["price"])
