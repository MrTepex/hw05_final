import shutil
import tempfile

from http import HTTPStatus

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from ..forms import CommentForm, PostForm
from ..models import Comment, Group, Post

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostFormsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user_1 = get_user_model().objects.create_user(username='Anne')
        cls.user_2 = get_user_model().objects.create_user(username='RandomMan')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test_slug',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user_1,
            text='Тестовый пост',
            group=cls.group,
        )
        cls.form = PostForm()

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client_1 = Client()
        self.authorized_client_1.force_login(self.user_1)
        self.authorized_client_2 = Client()
        self.authorized_client_2.force_login(self.user_2)

    def test_post_create_form(self):
        """Проверка работы редиректа, создания поста
         и наличия новой записи после ее создания """
        posts_amount = Post.objects.count()
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )
        form_data = {
            'text': 'Содержание только что созданного поста',
            'group': self.group.id,
            'image': uploaded
        }
        response = self.authorized_client_1.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True,
        )
        self.assertRedirects(response, reverse(
            'posts:profile', kwargs={'username': self.post.author}))
        self.assertEqual(Post.objects.count(), posts_amount + 1)
        self.assertTrue(Post.objects.filter(
            text='Содержание только что созданного поста',
            group=self.group,
            image='posts/small.gif'
        ).exists())
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_post_create_form_redirects_anonymous_to_login(self):
        """Проверка редиректа неавторизованного пользователя
         со страницы создания поста"""
        posts_amount = Post.objects.count()
        response = self.guest_client.post(reverse('posts:post_create'))
        self.assertRedirects(response, f"{reverse('users:login')}?next="
                                       f"{reverse('posts:post_create')}")
        self.assertNotEqual(Post.objects.count(), posts_amount + 1)

    def test_post_edit_form_works_properly(self):
        """Проверка работы PostForm при изменении текста в post_edit
        плюс редирект пользователя, который не авторизован
        или не является автором поста"""
        post = Post.objects.create(
            text='Старый текст',
            author=self.user_1
        )
        self.authorized_client_1.post(reverse(
            'posts:post_edit', kwargs={'post_id': post.id}),
            data={'text': 'Новый текст'},
            follow=True
        )
        self.assertEqual(Post.objects.get(id=post.id).text, 'Новый текст')
        self.assertRedirects(self.guest_client.get(
            reverse('posts:post_edit', kwargs={'post_id': 1})),
            f"{reverse('users:login')}?next="
            f"{reverse('posts:post_edit', kwargs={'post_id': 1})}")
        response = self.authorized_client_2.post(reverse(
            'posts:post_edit', kwargs={'post_id': post.id}),
            data={'text': 'Новый текст'},
            follow=True
        )
        self.assertRedirects(response, reverse('posts:post_detail',
                                               kwargs={'post_id': post.id}))

    def test_labels_and_help_texts(self):
        """Проверка labels и help_texts формы PostForm"""
        text_label = PostFormsTest.form.fields['text'].label
        text_help_text = PostFormsTest.form.fields['text'].help_text
        group_label = PostFormsTest.form.fields['group'].label
        group_help_text = PostFormsTest.form.fields['group'].help_text
        image_label = PostFormsTest.form.fields['image'].label
        image_help_text = PostFormsTest.form.fields['image'].help_text
        self.assertEqual(text_label, 'Содержание поста')
        self.assertEqual(text_help_text, 'Текст поста')
        self.assertEqual(group_label, 'Группа')
        self.assertEqual(
            group_help_text, 'Группа, к которой будет относиться пост')
        self.assertEqual(image_label, 'Картинка')
        self.assertEqual(image_help_text, 'Загрузите картинку')


class CommentFormsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = get_user_model().objects.create_user(username='Haha')
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост',
        )
        cls.form = CommentForm()

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_comment_form_redirects_anonymous_to_login(self):
        """Проверка редиректа неавторизованного пользователя
        со страницы комментария поста"""
        response = self.guest_client.post(reverse(
            'posts:add_comment', kwargs={'post_id': self.post.id}))
        self.assertRedirects(response, f"{reverse('users:login')}?next="
        f"{reverse('posts:add_comment', kwargs={'post_id': self.post.id})}")

    def test_comment_form_labels(self):
        text_label = CommentFormsTest.form.fields['text'].label
        self.assertEqual(text_label, 'Текст комментария')

    def test_comment_form_works_properly(self):
        self.authorized_client.post(reverse('posts:add_comment',
                                    kwargs={'post_id': self.post.id}),
                                    data={'text': 'Новый комментарий'})
        self.assertTrue(Comment.objects.filter(
            text='Новый комментарий',
            post=self.post
        ).exists())
