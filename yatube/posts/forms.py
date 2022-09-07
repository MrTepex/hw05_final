from django import forms

from .models import Comment, Post


class PostForm(forms.ModelForm):
    """Форма для создания новой записи"""
    class Meta:
        model = Post
        fields = ('text', 'group', 'image')
        labels = {
            'text': 'Содержание поста',
            'group': 'Группа',
            'image': 'Картинка'
        }
        help_texts = {
            'text': 'Текст поста',
            'group': 'Группа, к которой будет относиться пост',
            'image': 'Загрузите картинку'
        }


class CommentForm(forms.ModelForm):
    """Форма комментария"""
    class Meta:
        model = Comment
        fields = ('text',)
        labels = {'text': 'Текст комментария'}
