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

    def test_users_logout_url_uses_correct_template(self):
        """Проверка на правильный шаблон для страницы
         logout приложения users"""
        response = self.authorized_client.get(reverse('users:logout'))
        self.assertTemplateUsed(response, 'users/logged_out.html')

    def test_users_pages_uses_correct_templates(self):
        """Проверка на правильные шаблоны для страниц приложения users"""
        template_url_names = {
            reverse('users:signup'): 'users/signup.html',
            reverse('users:login'): 'users/login.html',
            reverse('users:password_change'):
                'users/password_change_form.html',
            reverse('users:password_change_done'):
                'users/password_change_done.html',
            reverse('users:password_reset'):
                'users/password_reset_form.html',
            reverse('users:password_reset_done'):
                'users/password_reset_done.html',
            reverse('users:password_reset_confirm',
                    kwargs={'uidb64': 1, 'token': 2}):
                'users/password_reset_confirm.html',
            reverse('users:password_reset_complete'):
                'users/password_reset_complete.html',
        }
        for address, template in template_url_names.items():
            with self.subTest(address=address):
                response = self.authorized_client.get(address)
                self.assertTemplateUsed(response, template,
                                        f'\033[1m"{address}" не использует '
                                        f'"{template}"\033[0m')
