from django.test import TestCase, Client
from django.contrib.auth import authenticate
from library.models import User

class AuthTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            role='reader'
        )

    def test_user_creation(self):
        self.assertEqual(self.user.username, 'testuser')
        self.assertEqual(self.user.role, 'reader')

    def test_user_has_perm(self):
        self.assertTrue(self.user.has_perm('reader.view_book'))
        self.assertFalse(self.user.has_perm('admin'))
        self.assertFalse(self.user.has_perm('guest.view_book'))

    def test_authentication(self):
        user = authenticate(username='testuser', password='testpass123')
        self.assertIsNotNone(user)
        self.assertEqual(user.role, 'reader')

print('Тесты пройдены успешно!')

