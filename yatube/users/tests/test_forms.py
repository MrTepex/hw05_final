from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse


class UsersURLTests(TestCase):

    def setUp(self):
        self.guest_client = Client()
        self.user = get_user_model().objects.create_user(
            username='Anne_Hathaway')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_signup_form_creates_new_user(self):
        """Проверка создания нового пользователя формой SignUp"""
        form_data = {
            'username': 'NewUser',
            'password1': 'QwErTy1234yTrEwQ',
            'password2': 'QwErTy1234yTrEwQ'
        }
        self.guest_client.post(reverse('users:signup'),
                               data=form_data,
                               follow=True
                               )
        self.assertTrue(get_user_model().objects.filter(
            username='NewUser').exists())
