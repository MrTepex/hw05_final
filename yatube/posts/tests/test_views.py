import datetime
import shutil
import tempfile

from django import forms
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django.db.models.fields.files import ImageFieldFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from ..forms import CommentForm
from ..models import Comment, Follow, Group, Post

User = get_user_model()
TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostViewsTest(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create(username='Hathaway')
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        cls.uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test_slug',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост',
            group=cls.group,
            pub_date=datetime.datetime.now,
            image=cls.uploaded
        )
        cls.comment = Comment.objects.create(
            post=cls.post,
            author=cls.user,
            text='Просто коммент',
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_pages_uses_correct_template(self):
        """Проверка на использование корректного шаблона"""
        cache.clear()
        templates_pages_names = {
            reverse('posts:index'): 'posts/index.html',
            reverse('posts:group_list', kwargs={'slug': 'test_slug'}):
                'posts/group_list.html',
            reverse('posts:profile', kwargs={'username': 'Hathaway'}):
                'posts/profile.html',
            reverse('posts:post_detail', kwargs={'post_id': self.post.id}):
                'posts/post_detail.html',
            reverse('posts:post_create'): 'posts/post_create.html',
            reverse('posts:post_edit', kwargs={'post_id': self.post.id}):
                'posts/post_create.html',
            reverse('posts:follow_index'): 'posts/follow.html',
        }
        for reverse_name, template in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_index_page_show_correct_context(self):
        """Проверка правильного контекста функции index"""
        cache.clear()
        response = self.authorized_client.get(reverse('posts:index'))
        obj = response.context['page_obj'][0]
        self.assertEqual(obj.text, 'Тестовый пост')
        self.assertEqual(obj.author, self.user)
        self.assertEqual(obj.group, self.group)
        self.assertIsInstance(obj.pub_date, datetime.datetime)
        self.assertIsInstance(obj.image, ImageFieldFile)

    def test_follow_index_page_show_correct_context(self):
        """Проверка правильного контекста функции index_follow"""
        post = Post.objects.create(author=User.objects.create(
            username='AAA'),
            text='1111',
            group=self.group
        )
        self.authorized_client.post(reverse(
            'posts:profile_follow', kwargs={'username': 'AAA'}))
        response = self.authorized_client.get(reverse('posts:follow_index'))
        obj = response.context['page_obj'][0]
        self.assertEqual(obj.text, post.text)
        self.assertEqual(obj.author, post.author)
        self.assertEqual(obj.group, post.group)
        self.assertIsInstance(obj.pub_date, datetime.datetime)
        self.assertIsInstance(obj.image, ImageFieldFile)

    def test_group_list_page_show_correct_context(self):
        """Проверка правильного контекста функции group_list"""
        response = self.authorized_client.get(
            reverse('posts:group_list', kwargs={'slug': 'test_slug'}))
        obj = response.context['page_obj'][0]
        self.assertEqual(obj.text, 'Тестовый пост')
        self.assertEqual(obj.author, self.user)
        self.assertEqual(obj.group, self.group)
        self.assertIsInstance(obj.pub_date, datetime.datetime)
        self.assertIsInstance(obj.image, ImageFieldFile)

    def test_profile_page_show_correct_context(self):
        """Проверка правильного контекста функции profile"""
        response = self.authorized_client.get(
            reverse('posts:profile', kwargs={'username': 'Hathaway'}))
        obj = response.context['page_obj'][0]
        self.assertEqual(response.context.get('author'), self.user)
        self.assertEqual(obj.text, 'Тестовый пост')
        self.assertEqual(obj.author, self.user)
        self.assertEqual(obj.group, self.group)
        self.assertIsInstance(obj.pub_date, datetime.datetime)
        self.assertIsInstance(obj.image, ImageFieldFile)

    def test_post_detail_page_show_correct_context(self):
        """Проверка правильного контекста функции post_detail"""
        response = self.authorized_client.get(
            reverse('posts:post_detail', kwargs={'post_id': self.post.id}))
        self.assertEqual(response.context.get('post'), self.post)
        self.assertEqual(response.context.get('group'), self.group)
        self.assertEqual(response.context.get('title_text'), 'Тестовый пост')
        self.assertEqual(response.context.get('author'), self.user)
        expected_comment_context = Comment.objects.filter(post_id=self.post.id)
        self.assertQuerysetEqual(response.context.get('comments'),
                                 map(repr, expected_comment_context))
        self.assertIsInstance(response.context.get('form'), CommentForm)

    def test_post_create_and_edit_page_show_correct_context(self):
        """Проверка правильного контекста функции post_create"""
        response = self.authorized_client.get(reverse('posts:post_create'))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context['form'].fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_pages_contains_correct_amount_of_posts(self):
        """Проверка правильного отображения пагинатором
        количества постов на страницах, а также
        правильность содержания постов"""
        cache.clear()
        Post.objects.bulk_create(
            Post(
                text=f'Текст поста №{i}', author=self.user, group=self.group
            ) for i in range(11)
        )

        response_index_1 = self.guest_client.get(reverse(
            'posts:index'))
        self.assertEqual(len(response_index_1.context['page_obj']), 10)
        response_index_2 = self.client.get(reverse(
            'posts:index') + '?page=2')
        self.assertEqual(len(response_index_2.context['page_obj']), 2)
        response_group_list_1 = self.guest_client.get(reverse(
            'posts:group_list', kwargs={'slug': 'test_slug'}))
        self.assertEqual(len(response_group_list_1.context['page_obj']), 10)
        response_group_list_2 = self.client.get(reverse(
            'posts:group_list', kwargs={'slug': 'test_slug'}) + '?page=2')
        self.assertEqual(len(response_group_list_2.context['page_obj']), 2)
        response_profile_1 = self.guest_client.get(reverse(
            'posts:profile', kwargs={'username': 'Hathaway'}))
        self.assertEqual(len(response_profile_1.context['page_obj']), 10)
        response_profile_2 = self.client.get(reverse(
            'posts:profile', kwargs={'username': 'Hathaway'}) + '?page=2')
        self.assertEqual(len(response_profile_2.context['page_obj']), 2)
        test_object = response_index_1.context['page_obj']
        for i in test_object:
            self.assertEqual(i.text, f'{i}')

    def test_additional_for_post_create(self):
        """Дополнительная проверка при создании поста"""
        cache.clear()
        Post.objects.create(
            author=self.user,
            group=Group.objects.create(
                title='Группа',
                slug='just_first_slug',
            ),
            text='Текст дополнительного теста'
        )
        response_1 = self.authorized_client.get(reverse('posts:index'))
        object_1 = response_1.context['page_obj'][0]
        self.assertEqual(object_1.text, 'Текст дополнительного теста')
        response_2 = self.authorized_client.get(reverse(
            'posts:profile', kwargs={'username': 'Hathaway'}))
        object_2 = response_2.context['page_obj'][0]
        self.assertEqual(object_2.text, 'Текст дополнительного теста')
        response_3 = self.authorized_client.get(reverse(
            'posts:group_list', kwargs={'slug': 'just_first_slug'}))
        object_3 = response_3.context['page_obj'][0]
        self.assertEqual(object_3.text, 'Текст дополнительного теста')

    def test_post_create_correct_group(self):
        """Проверка на правильное отношение вновь
         созданного поста в выбранной группе"""
        Post.objects.create(
            author=self.user,
            group=Group.objects.create(
                title='Группа для дополнительного теста_1',
                slug='just_first_slug',
            ),
            text='Текст дополнительного теста'
        )
        Post.objects.create(
            author=User.objects.create(username='MrX'),
            group=Group.objects.create(
                title='Группа для дополнительного теста_2',
                slug='just_second_slug',
            ),
            text='Вообще другой текст'
        )
        response_1 = self.authorized_client.get(reverse(
            'posts:group_list', kwargs={'slug': 'just_first_slug'}))
        object_1 = response_1.context['page_obj'][0]
        self.assertEqual(object_1.text, 'Текст дополнительного теста')
        response_2 = self.authorized_client.get(reverse(
            'posts:group_list', kwargs={'slug': 'just_second_slug'}))
        object_2 = response_2.context['page_obj'][0]
        self.assertNotEqual(object_1, object_2)

    def test_cache_works_properly(self):
        response_1 = self.authorized_client.get(reverse('posts:index'))
        result_1 = response_1.content
        Post.objects.filter(id=1).delete()
        response_2 = self.authorized_client.get(reverse('posts:index'))
        result_2 = response_2.content
        self.assertEqual(result_1, result_2)
        cache.clear()
        response_3 = self.authorized_client.get(reverse('posts:index'))
        result_3 = response_3.content
        self.assertNotEqual(result_1, result_3)
        self.assertNotEqual(result_2, result_3)

    def test_follow_works_properly(self):
        """Проверка, что авторизованный пользователь может подписываться
         на других пользователей и удалять их из подписок"""
        self.authorized_client_2 = User.objects.create(username='BBB')
        following_count = Follow.objects.all().count()
        Post.objects.create(author=User.objects.create(username='AAA'),
                            text='1111')
        self.authorized_client.post(reverse(
            'posts:profile_follow', kwargs={'username': 'AAA'}))
        self.assertEqual(Follow.objects.all().count(),
                         following_count + 1)
        self.assertNotEqual(Follow.objects.filter(
            user_id=self.authorized_client_2.id).count(), following_count + 1)
        self.authorized_client.post(reverse('posts:profile_unfollow',
                                            kwargs={'username': 'AAA'}))
        self.assertEqual(Follow.objects.all().count(), 0)
