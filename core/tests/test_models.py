from django.test import TestCase
from django.contrib.auth import get_user_model

from recipe.models import Tag, Ingredient, Recipe


def sample_user(email="example@email.com", password="testpass"):
    return get_user_model().objects.create_user(email, password)


class ModelTests(TestCase):
    def test_create_user_with_email_succussful(self):
        """Test creating a new user with email is succussful"""
        email = "example@email.com"
        password = "testpassword"
        user = get_user_model().objects.create_user(email=email, password=password)

        self.assertEquals(user.email, email)
        self.assertTrue(user.check_password(password))

    def test_new_user_email_normalized(self):
        """Test the email for new user is normalized"""
        email = "example@EMAIL.COM"
        user = get_user_model().objects.create_user(email=email)

        self.assertEqual(user.email, email.lower())

    def test_new_user_invalid_email(self):
        "Test creating a user with no email raises value error"
        with self.assertRaises(ValueError):
            get_user_model().objects.create_user(email=None)

    def test_create_superuser(self):
        """Test creating new superuser"""
        user = get_user_model().objects.create_superuser(
            "example@email.com", "password123"
        )

        self.assertTrue(user.is_staff)
        self.assertTrue(user.is_superuser)

    def test_tag_str(self):
        """Test that model str for Tag model is correct"""
        user = sample_user()
        tag = Tag.objects.create(user=user, name="Vegen")

        self.assertEqual(str(tag), tag.name)

    def test_ingredient_str(self):
        """Test string representation of Ingredient model"""
        ingredient = Ingredient.objects.create(user=sample_user(), name="ingretient1")

        self.assertEqual(str(ingredient), ingredient.name)

    def test_recipe_str(self):
        """Test the string representation of Recipe model"""
        recipe = Recipe.objects.create(
            user=sample_user(), title="recipe1", time_minutes=5, price=25
        )

        self.assertEqual(str(recipe), recipe.title)
