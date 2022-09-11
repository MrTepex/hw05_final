from django.contrib.auth import get_user_model
from django.test import TestCase

from ..models import Comment, Follow, Group, Post


class PostsModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = get_user_model().objects.create_user(
            username='Anne_Hathaway'
        )
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test_slug',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост',
        )

    def test_post_and_group_models_have_correct_object_names(self):
        """Проверка, что у моделей Post и Group корректно работают __str__."""
        group = PostsModelTest.group
        post = PostsModelTest.post
        expected_group_name = group.title
        expected_post_text = post.text[:15]
        self.assertEqual(expected_group_name, str(group))
        self.assertEqual(expected_post_text, str(post))

    def test_post_model_verbose_name(self):
        """Проверка корректности verbose_name атрибутов моделей Post, Group"""
        post = PostsModelTest.post
        field_verboses = {
            'text': 'Содержание поста',
            'pub_date': 'Дата и время поста',
            'group': 'Группа',
            'author': 'Автор',
            'image': 'Картинка',
        }
        for field, expected_value in field_verboses.items():
            with self.subTest(field=field):
                post_verbose = post._meta.get_field(field).verbose_name
                self.assertEqual(post_verbose, expected_value,
                                 f'verbose_name для "{field}" модели '
                                 f'"{post.__class__.__name__}" некорректно')


class CommentModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = get_user_model().objects.create_user(
            username='Anne_Hathaway'
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост',
        )
        cls.comment = Comment.objects.create(
            text='Новый комментарий',
            post=cls.post,
            author=cls.user
        )

    def test_comment_model_have_correct_object_names(self):
        """Проверка, что у модели Comment корректно работает __str__."""
        comment = CommentModelTest.comment
        expected_comment_text = comment.text[:30]
        self.assertEqual(expected_comment_text, str(comment))

    def test_comment_model_verbose_name(self):
        """Проверка корректности verbose_name атрибутов модели Comment"""
        comment = CommentModelTest.comment
        field_verboses = {
            'post': 'Пост',
            'author': 'Автор комментария',
            'text': 'Текст комментария',
            'created': 'Дата и время комментария',
        }
        for field, expected_value in field_verboses.items():
            with self.subTest(field=field):
                post_verbose = comment._meta.get_field(field).verbose_name
                self.assertEqual(post_verbose, expected_value,
                                 f'verbose_name для "{field}" модели '
                                 f'"{comment.__class__.__name__}" некорректно')


class FollowModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = get_user_model().objects.create_user(
            username='Anne_Hathaway'
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост',
        )
        cls.following = Follow.objects.create(
            user_id=cls.user.id,
            author_id=1
        )

    def test_comment_model_verbose_name(self):
        """Проверка корректности verbose_name атрибутов модели Comment"""
        flwng = self.following
        field_verboses = {
            'user': 'Подписчик',
            'author': 'Автор',
        }
        for field, expected_value in field_verboses.items():
            with self.subTest(field=field):
                post_verbose = flwng._meta.get_field(field).verbose_name
                self.assertEqual(post_verbose, expected_value,
                                 f'verbose_name для "{field}" модели '
                                 f'"{flwng.__class__.__name__}" некорректно')
