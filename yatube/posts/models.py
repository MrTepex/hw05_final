from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class Group(models.Model):
    """Модель для сообществ (групп)"""
    title = models.CharField(max_length=200,
                             verbose_name='Заголовок вкладки')
    slug = models.SlugField(unique=True,
                            verbose_name='Относительный адрес')
    description = models.TextField(max_length=700,
                                   verbose_name='Описание группы')

    class Meta:
        verbose_name = 'Группа'
        verbose_name_plural = 'Группы'

    def __str__(self):
        return self.title


class Post(models.Model):
    """Модель для создания постов"""
    text = models.TextField(verbose_name='Содержание поста')
    pub_date = models.DateTimeField(auto_now_add=True,
                                    verbose_name='Дата и время поста')
    author = models.ForeignKey(User,
                               on_delete=models.CASCADE,
                               related_name='posts',
                               verbose_name='Автор')
    group = models.ForeignKey(Group,
                              on_delete=models.SET_NULL,
                              related_name='posts',
                              verbose_name='Группа',
                              blank=True,
                              null=True)
    image = models.ImageField(
        verbose_name='Картинка',
        upload_to='posts/',
        blank=True,
    )

    class Meta:
        ordering = ['-pub_date']
        verbose_name = 'Пост'
        verbose_name_plural = 'Посты'

    def __str__(self):
        return self.text[:15]


class Comment(models.Model):
    """Модель для комментариев к записям"""
    post = models.ForeignKey(Post,
                             on_delete=models.CASCADE,
                             related_name='comments',
                             verbose_name='Пост',
                             blank=True)

    author = models.ForeignKey(User,
                               on_delete=models.CASCADE,
                               related_name='comments',
                               verbose_name='Автор комментария')
    text = models.TextField(verbose_name='Текст комментария')
    created = models.DateTimeField(auto_now_add=True,
                                   verbose_name='Дата и время комментария')

    class Meta:
        ordering = ['-created']
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'

    def __str__(self):
        return self.text[:30]


class Follow(models.Model):
    """Модель для подписок"""
    user = models.ForeignKey(User,
                             on_delete=models.CASCADE,
                             related_name='follower',
                             verbose_name='Подписчик'
                             )
    author = models.ForeignKey(User,
                               on_delete=models.CASCADE,
                               related_name='following',
                               verbose_name='Автор',
                               )

    class Meta:
        unique_together = ['user', 'author']
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
