from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Tag, Recipe

from recipe.serializers import TagSerializer


TAGS_URL = reverse("recipe:tag-list")


class PublicTagsAPITests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_login_required(self):

        res = self.client.get(TAGS_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateTagsAPITests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            email="nilo@email.com", name="Nilo Neto"
        )
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def test_retrieve_tags(self):
        Tag.objects.create(user=self.user, name="Vegan")
        Tag.objects.create(user=self.user, name="Desert")

        res = self.client.get(TAGS_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        tags = Tag.objects.all().order_by("-name")
        serializer = TagSerializer(tags, many=True)

        self.assertEqual(res.data, serializer.data)

    def test_tags_are_limited_to_user(self):
        self.user2 = get_user_model().objects.create_user(
            email="nilo2@email.com", name="Nilo Neto 2"
        )

        Tag.objects.create(user=self.user, name="Vegan")
        Tag.objects.create(user=self.user2, name="Main")

        res = self.client.get(TAGS_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        self.assertEqual(len(res.data), 1)

        self.assertEqual(res.data[0]["name"], "Vegan")

    def test_create_tag_successful(self):
        payload = {
            "name": "Test Tag",
        }

        self.client.post(TAGS_URL, payload)

        exists = Tag.objects.filter(user=self.user, name=payload["name"]).exists()

        self.assertTrue(exists)

    def test_create_invalid_tag(self):

        payload = {"name": ""}

        res = self.client.post(TAGS_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_retrieve_tags_assigned_to_recipes(self):
        tag1 = Tag.objects.create(user=self.user, name="Desert")
        tag2 = Tag.objects.create(user=self.user, name="Lunch")
        recipe = Recipe.objects.create(
            title="Recipe 1", time_minutes=5, price=11.90, user=self.user
        )
        recipe.tags.add(tag1)

        res = self.client.get(TAGS_URL, {"assigned_only": 1})

        serializer_tag_1 = TagSerializer(tag1)
        serializer_tag_2 = TagSerializer(tag2)

        self.assertIn(serializer_tag_1.data, res.data)
        self.assertNotIn(serializer_tag_2.data, res.data)

    def test_retrieve_tags_assigned_are_unique(self):
        tag = Tag.objects.create(user=self.user, name="Desert")
        Tag.objects.create(user=self.user, name="Lunch")
        recipe = Recipe.objects.create(
            title="Recipe 1", time_minutes=5, price=11.90, user=self.user
        )
        recipe.tags.add(tag)

        recipe2 = Recipe.objects.create(
            title="Recipe 2", time_minutes=5, price=11.90, user=self.user
        )
        recipe2.tags.add(tag)

        res = self.client.get(TAGS_URL, {"assigned_only": 1})

        self.assertEqual(len(res.data), 1)
