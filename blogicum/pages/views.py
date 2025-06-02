# blogicum/pages/views.py
from django.shortcuts import render


def about(request):
    # Функция-обработчик для страницы 'О нас'
    # Имя шаблона: about.html
    return render(request, "pages/about.html")


def rules(request):
    # Функция-обработчик для страницы 'Правила'
    # Имя шаблона: rules.html
    return render(request, "pages/rules.html")
