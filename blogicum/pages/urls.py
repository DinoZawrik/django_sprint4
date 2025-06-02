# blogicum/pages/urls.py
from django.urls import path
from . import views

app_name = "pages"  # Пространство имен для приложения

urlpatterns = [
    path("about/", views.about, name="about"),  # Имя маршрута 'about'
    path("rules/", views.rules, name="rules"),  # Имя маршрута 'rules'
]
