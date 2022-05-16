from genericpath import exists
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

from recipe.models import Tag
from recipe.serializers import TagSerializer

from rest_framework.test import APIClient
from rest_framework import status

TAGS_URL = reverse("recipe:tag-list")


class PublicTagsApiTest(TestCase):
    """Tests for publicly available tags APIs"""

    def setUp(self):
        self.client = APIClient()

    def test_login_required(self):
        """Test that login is required to retrive tags"""
        res = self.client.get(TAGS_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateTagsApiTest(TestCase):
    """Tests for tags APIs - Authorized"""

    def setUp(self):
        self.user = get_user_model().objects.create_user(
            "example@email.com", "testpass"
        )
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def test_retrive_tags(self):
        """Test that retriving tags is successful"""
        Tag.objects.create(user=self.user, name="Fruity")

        res = self.client.get(TAGS_URL)

        tags = Tag.objects.all()
        serializer = TagSerializer(tags, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_tags_limited_to_user(self):
        """Test that retrived tags are limited to a user"""
        user2 = get_user_model().objects.create_user("example2@email.com", "testpass")
        Tag.objects.create(user=user2, name="Fruity")
        Tag.objects.create(user=self.user, name="Desert")

        res = self.client.get(TAGS_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)

    def test_create_tag_successful(self):
        """Test that creating a new tag is successful"""
        payload = {"name": "Fruity"}
        self.client.post(TAGS_URL, payload)

        is_tag_exists = Tag.objects.filter(
            user=self.user, name=payload["name"]
        ).exists()

        self.assertTrue(is_tag_exists)

    def test_create_tag_invalid(self):
        """Test that create a new tag with invalid payload fails"""
        payload = {"name": ""}
        res = self.client.post(TAGS_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
