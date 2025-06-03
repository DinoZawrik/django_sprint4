# blogicum/blog/urls.py
from django.urls import path
from . import views

app_name = "blog"

urlpatterns = [
    path("", views.index, name="index"),
    path("posts/<int:post_id>/", views.post_detail, name="post_detail"),
    path(
        "category/<slug:slug>/",
        views.category_posts,
        name="category_posts",
    ),
    path("posts/create/", views.PostCreateView.as_view(), name="post_create"),
    path(
        "posts/<int:post_id>/edit/",
        views.PostUpdateView.as_view(),
        name="post_edit",
    ),
    path("posts/<int:post_id>/comment/", views.add_comment, name="add_comment"),
    path(
        "posts/<int:post_id>/delete/",
        views.PostDeleteView.as_view(),
        name="post_delete",
    ),
]

urlpatterns += [
    path(
        "posts/<int:post_id>/edit_comment/<int:comment_id>/",
        views.CommentUpdateView.as_view(),
        name="edit_comment",
    ),
    path(
        "posts/<int:post_id>/delete_comment/<int:comment_id>/",
        views.CommentDeleteView.as_view(),
        name="delete_comment",
    ),
    path(
        "profile/<str:username>/",
        views.profile_detail,
        name="profile_detail",
    ),
    path(
        "profile/<str:username>/edit/",
        views.edit_profile,
        name="edit_profile",
    ),
]
