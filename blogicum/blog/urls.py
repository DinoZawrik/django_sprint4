# blogicum/blog/urls.py
from django.urls import path
from . import views

app_name = "blog"

urlpatterns = [
    path("", views.index, name="index"),
    path("posts/<int:pk>/", views.post_detail, name="post_detail"),
    path(
        "category/<slug:slug>/",
        views.category_posts,
        name="category_posts",
    ),
]

urlpatterns += [
    path('profile/<str:username>/', views.profile_detail, name='profile_detail'), # <--- Добавьте
]
