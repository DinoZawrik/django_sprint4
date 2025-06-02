# blogicum/pages/urls.py
from django.urls import path
from . import views

app_name = "pages"  # Пространство имен для приложения

urlpatterns = [
    path("author/", views.AuthorView.as_view(), name="author"),
    path("tech/", views.TechView.as_view(), name="tech"),
    # Имя маршрута 'about'
    path("about/", views.AboutView.as_view(), name="about"),
    # Имя маршрута 'rules'
    path("rules/", views.RulesView.as_view(), name="rules"),
]
