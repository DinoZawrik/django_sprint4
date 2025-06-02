from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import Post, Comment # Импортируем для форм

class CreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        fields = ('first_name', 'last_name', 'username', 'email')

class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ('title', 'text', 'category', 'location', 'image') # Добавьте image!

    pub_date = forms.DateTimeField(required=False)

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('text',)