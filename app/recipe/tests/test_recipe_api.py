from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from core.models import Recipe, Tag, Ingredient
from recipe.serializers import RecipeSerializer, RecipeDetailSerializer

RECIPE_URL = reverse('recipe:recipe-list')


def detail_url(recipe_id):
    return reverse('recipe:recipe-detail', args=[recipe_id])


def create_sample_tag(user, name='sample tag'):
    return Tag.objects.create(user=user, name=name)


def create_sample_ingredient(user, name='sample ingredient'):
    return Ingredient.objects.create(user=user, name=name)


def create_sample_recipe(user, **kwargs):
    """Create and returns sample recipe"""
    defaults = {
        'title': 'Sample Recipe',
        'time_minutes': 10,
        'price': 5.00
    }
    defaults.update(kwargs)

    return Recipe.objects.create(user=user, **defaults)


class PublicRecipeAPITests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_unauthorized_access(self):
        res = self.client.get(RECIPE_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateRecipeAPITests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            'nilo@gmail.com',
            '123456'
        )
        self.client.force_authenticate(self.user)

    def test_retrieving_recipes(self):
        create_sample_recipe(self.user)
        create_sample_recipe(self.user)

        res = self.client.get(RECIPE_URL)
        recipes = Recipe.objects.all().order_by('-id')
        serializer = RecipeSerializer(recipes, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_recipes_limited_to_user(self):
        user2 = get_user_model().objects.create_user(
            'other@gmail.com',
            '1234567'
        )

        create_sample_recipe(self.user)
        create_sample_recipe(user2)

        res = self.client.get(RECIPE_URL)
        recipes = Recipe.objects.filter(user=self.user)
        serializer = RecipeSerializer(recipes, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data, serializer.data)

    def test_view_recipe_detail(self):
        recipe = create_sample_recipe(self.user)
        recipe.tags.add(create_sample_tag(user=self.user))
        recipe.ingredients.add(create_sample_ingredient(user=self.user))

        res = self.client.get(detail_url(recipe.id))
        serializer = RecipeDetailSerializer(recipe)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_create_basic_recipe(self):
        payload = {
            'title': 'chocolate chessecake',
            'time_minutes': 30,
            'price': 5.50
        }

        res = self.client.post(RECIPE_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        recipe = Recipe.objects.get(id=res.data['id'])

        for key in payload.keys():
            if key == 'price':
                self.assertEqual(
                    float(res.data[key]), float(getattr(recipe, key)))
            else:
                self.assertEqual(res.data[key], getattr(recipe, key))

    def test_create_recipe_with_tags(self):
        tag1 = create_sample_tag(user=self.user, name='Vegan')
        tag2 = create_sample_tag(user=self.user, name='Desert')
        payload = {
            'title': 'Avocado Chessecake',
            'tags': [tag1.id, tag2.id],
            'time_minutes': 20,
            'price': 6.50
        }

        res = self.client.post(RECIPE_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        recipe = Recipe.objects.get(id=res.data['id'])
        tags = recipe.tags.all()

        self.assertEqual(tags.count(), 2)
        self.assertIn(tag1, tags)
        self.assertIn(tag2, tags)

    def test_create_recipe_with_ingredients(self):
        ing1 = create_sample_ingredient(user=self.user, name='Onion')
        ing2 = create_sample_ingredient(user=self.user, name='Ginger')
        payload = {
            'title': 'Same recipe',
            'ingredients': [ing1.id, ing2.id],
            'time_minutes': 20,
            'price': 7.50,
            'link': 'https://recipes.com/recipe2'
        }

        res = self.client.post(RECIPE_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        recipe = Recipe.objects.get(id=res.data['id'])
        ingredients = recipe.ingredients.all()
        self.assertEqual(ingredients.count(), 2)
        self.assertIn(ing1, ingredients)
        self.assertIn(ing2, ingredients)

    def test_recipe_partial_update(self):
        """Test update recipe with PATCH"""
        recipe = create_sample_recipe(user=self.user, price=2)
        recipe.tags.add(create_sample_tag(user=self.user))

        new_tag = create_sample_tag(user=self.user, name='Curry')
        payload = {
            'title': 'Apple Pie',
            'tags': [new_tag.id]
        }

        self.client.patch(detail_url(recipe.id), payload)

        recipe.refresh_from_db()

        self.assertEqual(recipe.title, payload['title'])
        tags = recipe.tags.all()
        self.assertEqual(len(tags), 1)
        self.assertIn(new_tag, tags)
        self.assertEqual(recipe.price, 2)

    def test_recipe_full_update(self):
        """Test update recipe with PUT"""
        recipe = create_sample_recipe(user=self.user)
        recipe.tags.add(create_sample_tag(user=self.user))
        payload = {
            'title': 'Apple Pie',
            'time_minutes': 25,
            'price': 20
        }
        self.client.put(detail_url(recipe.id), payload)

        recipe.refresh_from_db()
        tags = recipe.tags.all()

        self.assertEqual(recipe.title, payload['title'])
        self.assertEqual(recipe.time_minutes, payload['time_minutes'])
        self.assertEqual(recipe.price, payload['price'])
        self.assertEqual(len(tags), 0)
