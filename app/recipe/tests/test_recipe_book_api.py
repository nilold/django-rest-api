from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from core.models import RecipeBook, Recipe
from recipe.serializers import RecipeBookSerializer

RECIPE_BOOK_URL = reverse('recipe:recipebook-list')


def create_sample_recipe(user, **kwargs):
    defaults = {
        'title': 'Cheesecake',
        'time_minutes': 5,
        'price': 8.00
    }
    defaults.update(kwargs)
    recipe = Recipe.objects.create(user=user, **defaults)

    return recipe


class PublicRecipeBookAPITests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_forbidden_access(self):
        res = self.client.get(RECIPE_BOOK_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateRecipeBookAPITests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create(
            email='test@test.com',
            password='1234567'
        )
        self.client.force_authenticate(self.user)

    def test_get_recipe_book_list(self):
        recipe_book = RecipeBook.objects.create(
            user=self.user,
            title='My Book'
        )
        recipe_book.recipes.add(create_sample_recipe(self.user))
        serialized_rb = RecipeBookSerializer(recipe_book)

        res = self.client.get(RECIPE_BOOK_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data[0], serialized_rb.data)
