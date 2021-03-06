from django.test import TestCase
from django.contrib.auth import get_user_model
from core import models
from unittest.mock import patch


def sample_user(email="test@gmail.com", password="1234567"):
    return get_user_model().objects.create_user(email=email, password=password)


class ModelTests(TestCase):
    def test_crate_user_with_email_sucessfull(self):
        """"Teste creating a new user with and email is successful"""
        email = "nilo@nilo.com"
        password = "12345"

        user = get_user_model().objects.create_user(email=email, password=password)

        self.assertEqual(email, user.email)
        self.assertTrue(user.check_password(password))

    def test_new_user_email_normalized(self):
        """Test email for a new user is normalized"""

        email = "nilo@NILO.coM"

        user = get_user_model().objects.create_user(email=email, password="12345")

        self.assertEqual(email.lower(), user.email)

    def test_new_user_invalid_email(self):
        """Test create user with no email raises error"""

        with self.assertRaises(ValueError):
            get_user_model().objects.create_user(email=None, password="12324")

    def test_create_new_superuser(self):
        """Test creating nre superuser"""

        user = get_user_model().objects.create_superuser("nilo@superuser.com", "12345")

        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)

    def test_tag_str(self):
        """Test tag string representation"""

        tag = models.Tag.objects.create(user=sample_user(), name="Vegan")

        self.assertEqual(str(tag), tag.name)

    def test_ingredient_str(self):
        ingredient = models.Ingredient.objects.create(
            user=sample_user(), name="Cucumber"
        )

        self.assertEqual(str(ingredient), ingredient.name)

    def test_recipe_str(self):
        recipe = models.Recipe.objects.create(
            user=sample_user(), title="Cheesecake", time_minutes=5, price=8.00
        )

        self.assertEqual(str(recipe), recipe.title)

    def test_recipe_book_str(self):
        user = sample_user()
        recipe_book = models.RecipeBook.objects.create(
            user=user, title="My Favourite Deserts",
        )
        recipe = models.Recipe.objects.create(
            user=user, title="Cheesecake", time_minutes=5, price=8.00
        )
        recipe_book.recipes.add(recipe)

        self.assertEqual(str(recipe_book), recipe_book.title)

    @patch("uuid.uuid4")
    def test_recipe_filename_uuid(self, mock_uuid):
        uuid = "mock_uuid"
        mock_uuid.return_value = uuid
        file_path = models.recipe_image_file_path(None, "my_image.jpg")
        expect_path = f"upload/recipe/{uuid}.jpg"

        self.assertEqual(expect_path, file_path)
