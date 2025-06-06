from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import Post, Comment  # Импортируем для форм

# Импортируем модель пользователя
from django.contrib.auth import get_user_model

User = get_user_model()


class CreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        fields = ("first_name", "last_name", "username", "email")


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = (
            "title",
            "text",
            "pub_date",
            "category",
            "location",
            "image",
            "is_published",
        )


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ("text",)


class ProfileEditForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ("first_name", "last_name", "username", "email")
