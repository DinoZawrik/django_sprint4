# blogicum/pages/views.py
from django.shortcuts import render
from django.views.generic import TemplateView


def about(request):
    # Функция-обработчик для страницы 'О нас'
    # Имя шаблона: about.html
    return render(request, "pages/about.html")


def rules(request):
    # Функция-обработчик для страницы 'Правила'
    # Имя шаблона: rules.html
    return render(request, "pages/rules.html")

class AuthorView(TemplateView):
    template_name = 'pages/author.html'

class TechView(TemplateView):
    template_name = 'pages/tech.html'
