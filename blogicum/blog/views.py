from django.shortcuts import get_object_or_404, render
from django.utils import timezone  # Работа с датой и временем
from django.http import Http404  # Генерация ошибки 404
from .models import Post, Category  # Импорт моделей
from django.contrib.auth.forms import UserCreationForm
from django.urls import reverse_lazy
from django.views.generic import CreateView
from django.contrib.auth import get_user_model
from django.core.paginator import Paginator # Для пагинации
from .forms import CreationForm # Импортируем новую форму

User = get_user_model() # В начале файла


def index(request):
    # Получаем 5 последних опубликованных постов из опубликованных
    # категорий, дата публикации которых не позже текущего времени.
    # select_related() используется для оптимизации запросов
    posts = (
        Post.objects.select_related("category", "author", "location")
        .filter(
            is_published=True,  # Пост опубликован
            pub_date__lte=timezone.now(),  # Дата публикации не позже текущего
            category__is_published=True,  # Категория поста опубликована
            # (исключает посты с category=None)
        )
        .order_by("-pub_date")[:5]
    )  # Сортируем по дате публикации по убыванию и берем 5 первых

    context = {
        "posts": posts,
    }
    return render(request, "blog/index.html", context)


def category_posts(request, slug):
    # Получаем объект категории по slug.
    # Если категория не найдена или не опубликована, возвращаем 404.
    category = get_object_or_404(Category, slug=slug, is_published=True)

    # Получаем посты выбранной категории, опубликованные,
    # и дата публикации которых не позже текущего времени.
    posts = (
        Post.objects.select_related("author", "location")
        .filter(
            category=category,  # Посты принадлежат данной категории
            is_published=True,  # Пост опубликован
            pub_date__lte=timezone.now(),  # Дата публикации не позже текущего
        )
        .order_by("-pub_date")
    )

    context = {
        "category": category,
        "posts": posts,
    }
    return render(request, "blog/category.html", context)


def post_detail(request, pk):
    # Получаем объект поста по первичному ключу (pk).
    # Используем select_related для оптимизации доступа к связанным
    # объектам в шаблоне.
    post = get_object_or_404(
        Post.objects.select_related("category", "author", "location"), pk=pk
    )

    # Проверяем условия для возврата ошибки 404:
    # 1. Дата публикации позже текущего времени
    # 2. Пост не опубликован
    # 3. Категория поста отсутствует ИЛИ категория поста не опубликована
    if (
        post.pub_date > timezone.now()
        or not post.is_published
        or (post.category is None or not post.category.is_published)
    ):
        raise Http404("Публикация не найдена или не опубликована.")

    context = {
        "post": post,
    }
    return render(request, "blog/detail.html", context)
