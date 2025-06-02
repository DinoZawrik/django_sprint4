from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import Post, Comment, Category, Location # Импортируем для форм

class CreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        fields = ('first_name', 'last_name', 'username', 'email')

class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ('title', 'text', 'pub_date', 'category', 'location', 'image') # Добавьте image!

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('text',)