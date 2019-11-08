from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status

CREATE_USER_URL = reverse('user:create')
TOKEN_URL = reverse('user:token')
ME_URL = reverse('user:me')


def create_user(**kwargs):
    return get_user_model().objects.create_user(**kwargs)


class PublicUserAPITests(TestCase):
    """tests the user api public"""

    def setUp(self):
        self.client = APIClient()

    def test_create_valid_user_is_successful(self):
        payload = {
            'email': 'nilo@test.com',
            'password': '1234567',
            'name': 'Test Name'
        }

        res = self.client.post(CREATE_USER_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        user = get_user_model().objects.get(**res.data)
        self.assertTrue(user.check_password(payload['password']))
        self.assertNotIn('password', res.data)

    def test_creating_a_existing_user_fails(self):
        payload = {
            'email': 'nilo@test.com',
            'password': '1234567',
            'name': 'Test Name'
        }
        create_user(**payload)

        res = self.client.post(CREATE_USER_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_password_too_short(self):
        """Password must be more than 5 charcters"""

        payload = {
            'email': 'nilo@test.com',
            'password': '123',
            'name': 'Test Name'
        }

        res = self.client.post(CREATE_USER_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

        user_exists = get_user_model().objects.filter(
            email=payload['email']
        ).exists()

        self.assertFalse(user_exists)

    def test_invalid_email(self):
        """User must have valid email address"""

        payload = {
            'email': 'nilo.com',
            'password': '1234567',
            'name': 'Test Name'
        }

        res = self.client.post(CREATE_USER_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

        user_exists = get_user_model().objects.filter(name=payload['name'])\
            .exists()
        self.assertFalse(user_exists)

    def test_retrieve_user_unauthorized(self):
        """Authentication is required for users"""

        res = self.client.get(ME_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateUserAPITests(TestCase):
    """Test APIs that require authentication"""

    def setUp(self):
        self.user = create_user(
            email='test_user@gmail.com',
            password='12345678',
            name='Some User'
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_retrieve_profile_success(self):
        """Test retrieve profile for logged in user"""

        res = self.client.get(ME_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, {
            'name': self.user.name,
            'email': self.user.email
        })

    def test_post_not_allowed(self):
        res = self.client.post(ME_URL, {})
        self.assertEqual(res.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_update_user_profile(self):
        payload = {'name': 'new name', 'password': 'new password'}
        res = self.client.patch(ME_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        self.user.refresh_from_db()

        self.assertEqual(self.user.name, payload['name'])
        self.assertTrue(self.user.check_password(payload['password']))
