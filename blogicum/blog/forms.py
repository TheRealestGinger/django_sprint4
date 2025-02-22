from django import forms
from django.contrib.auth import get_user_model

from .models import Post, Comment


User = get_user_model()


class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email')


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        exclude = ('author', 'is_published', 'comment_count')
        widgets = {
            'pub_date': forms.DateTimeInput(attrs={'type': 'datetime-local'})
        }


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('text',)
