from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Ingredient
from recipe.serializers import IngredientSerializer

INGREDIENT_URL = reverse('recipe:ingredient-list')


class PublicIngredientAPITests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_login_required(self):
        res = self.client.get(INGREDIENT_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateIngredientAPITests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            email='nilo@email.com',
            name='Nilo Neto'
        )
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def test_retrive_ingredients_list(self):
        Ingredient.objects.create(user=self.user, name='Kale')
        Ingredient.objects.create(user=self.user, name='Salt')

        res = self.client.get(INGREDIENT_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        ingredients = Ingredient.objects.all().order_by('-name')
        serializer = IngredientSerializer(ingredients, many=True)

        self.assertEqual(res.data, serializer.data)

    def test_ingredients_limited_to_user(self):
        user2 = get_user_model().objects.create_user(
            email='nilo2@nilo.com',
            password='123456'
        )

        ingredient = Ingredient.objects.create(user=self.user, name='Kale')
        Ingredient.objects.create(user=user2, name='Salt')

        res = self.client.get(INGREDIENT_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]['name'], ingredient.name)

    def test_creating_ingredients_successful(self):
        payload = {'name': 'Orange'}

        res = self.client.post(INGREDIENT_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        exists = Ingredient.objects\
            .filter(user=self.user, name=payload['name']).exists()
        self.assertTrue(exists)

    def test_create_invalid_ingredient(self):
        payload = {'name': ''}
        res = self.client.post(INGREDIENT_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
