from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.test import Client, TestCase
from django.shortcuts import reverse

from ..models import Group, Post


class PostURLTests(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = get_user_model().objects.create_user(
            username='Anne_Hathaway'
        )
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test_slug',
            description='Описание'
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый текст',
            group=cls.group,
        )

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_posts_urls_exists_at_desired_location_for_everybody(self):
        """Проверка отклика страниц приложения posts"""
        urls = {
            '/': HTTPStatus.OK,
            '/group/test_slug/': HTTPStatus.OK,
            '/profile/Anne_Hathaway/': HTTPStatus.OK,
            '/posts/1/': HTTPStatus.OK,
            '/posts/1/edit/': HTTPStatus.FOUND,
            '/create/': HTTPStatus.FOUND,
            '/unexisting_page/': HTTPStatus.NOT_FOUND,
        }
        for address, status in urls.items():
            with self.subTest(address=address):
                response = self.guest_client.get(address)
                self.assertEqual(response.status_code, status)

    def test_posts_create_url_redirect_anonymous_on_login(self):
        """Проверка редиректа неавторизованного пользователя
        со страницы создания поста на страницу "войти" """
        response = self.guest_client.get('/create/', follow=True)
        self.assertRedirects(response, '/auth/login/?next=/create/')

    def test_posts_edit_url_redirect_anonymous_on_login(self):
        """Проверка редиректа неавторизованного пользователя
        со страницы изменения поста на страницу "войти" """
        response = self.guest_client.get('/posts/1/edit/', follow=True)
        self.assertRedirects(response, '/auth/login/?next=/posts/1/edit/')

    def test_profile_follow_url_redirect_anonymous_on_login(self):
        """Проверка редиректа неавторизованного пользователя
        со страницы подписки на страницу "войти" """
        response = self.guest_client.get('/profile/1/follow/', follow=True)
        self.assertRedirects(response, '/auth/login/?next=/profile/1/follow/')

    def test_profile_unfollow_url_redirect_anonymous_on_login(self):
        """Проверка редиректа неавторизованного пользователя
        со страницы подписки на страницу "войти" """
        response = self.guest_client.get('/profile/1/unfollow/', follow=True)
        self.assertRedirects(response,
                             '/auth/login/?next=/profile/1/unfollow/')

    def test_posts_urls_uses_correct_templates(self):
        """Проверка на правильные шаблоны для страниц приложения users"""
        cache.clear()
        templates_url_names = {
            '/': 'posts/index.html',
            '/group/test_slug/': 'posts/group_list.html',
            '/profile/Anne_Hathaway/': 'posts/profile.html',
            '/posts/1/': 'posts/post_detail.html',
            '/posts/1/edit/': 'posts/post_create.html',
            '/create/': 'posts/post_create.html',
            '/follow/': 'posts/follow.html',
        }
        for address, template in templates_url_names.items():
            with self.subTest(address=address):
                response = self.authorized_client.get(address)
                self.assertTemplateUsed(response, template)

    def test_posts_comment_url_redirect_user_properly(self):
        """Проверка редиректа авторизованного пользователя при комментарии"""
        response = self.authorized_client.get(
            '/posts/1/comment/', follow=True)
        self.assertRedirects(response, '/posts/1/')

    def test_posts_comment_url_redirect_anonymous_on_login(self):
        """Проверка редиректа неавторизованного пользователя
        со страницы комментария поста на страницу "войти" """
        response = self.guest_client.get('/posts/1/comment/', follow=True)
        self.assertRedirects(response, '/auth/login/?next=/posts/1/comment/')
