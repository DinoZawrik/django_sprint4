from django.shortcuts import get_object_or_404, render
from django.utils import timezone  # Работа с датой и временем
from django.http import Http404  # Генерация ошибки 404
from .models import Post, Category, Comment  # Импорт моделей
from django.urls import reverse_lazy
from django.views.generic import CreateView, UpdateView, DeleteView # Для CBV
from django.contrib.auth import get_user_model
from .forms import PostForm, CommentForm # Импортируем формы
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin # Для CBV и проверки прав
from django.shortcuts import redirect # Для ручных редиреков
from django.db.models import Count # В views.py


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
        .annotate(comment_count=Count('comments')) # Добавляем количество комментариев
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
        .annotate(comment_count=Count('comments')) # Добавляем количество комментариев
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


    comment_form = CommentForm()
    context = {
        'post': post,
        'comment_form': comment_form, # Добавьте это
    }
    return render(request, 'blog/detail.html', context)

def profile_detail(request, username):
    # Получаем объект пользователя по username.
    # Если пользователь не найден, возвращаем 404.
    profile = get_object_or_404(User, username=username)

    # Получаем посты автора, опубликованные,
    # и дата публикации которых не позже текущего времени.
    posts = (
        profile.posts.select_related("category", "location")
        .filter(
            is_published=True,  # Пост опубликован
            pub_date__lte=timezone.now(),  # Дата публикации не позже текущего
            category__is_published=True,  # Категория поста опубликована
        )
        .annotate(comment_count=Count('comments')) # Добавляем количество комментариев
        .order_by("-pub_date")
    )

    context = {
        "profile": profile,
        "posts": posts,
    }
    return render(request, "blog/profile.html", context)


class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    form_class = PostForm
    template_name = 'blog/create.html'

    def form_valid(self, form):
        form.instance.author = self.request.user # Автоматически устанавливаем автора
        return super().form_valid(form)

    def get_success_url(self):
        # Перенаправление на страницу профиля автора
        return reverse_lazy('blog:profile_detail', kwargs={'username': self.request.user.username})


class PostUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Post
    form_class = PostForm
    template_name = 'blog/create.html' # Переиспользуем шаблон создания

    def test_func(self):
        # Проверка, что текущий пользователь - автор поста
        post = self.get_object()
        return self.request.user == post.author

    def handle_no_permission(self):
        # Если пользователь не автор, перенаправляем на страницу поста
        post = self.get_object()
        return redirect('blog:post_detail', pk=post.pk)

    def get_success_url(self):
        # После редактирования перенаправляем на страницу поста
        return reverse_lazy('blog:post_detail', kwargs={'pk': self.get_object().pk})

@login_required
def add_comment(request, pk):
    post = get_object_or_404(Post, pk=pk)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
        return redirect('blog:post_detail', pk=pk)
    context = {
        'post': post,
        'form': form,
    }
    return render(request, 'blog/detail.html', context) # Можно рендерить обратно detail.html

class PostDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Post
    template_name = 'blog/post_confirm_delete.html' # Создайте этот шаблон
    
    def test_func(self):
        # Проверка, что текущий пользователь - автор поста
        post = self.get_object()
        return self.request.user == post.author
    
    def handle_no_permission(self):
        # Если пользователь не автор, перенаправляем на страницу поста
        post = self.get_object()
        return redirect('blog:post_detail', pk=post.pk)

    def get_success_url(self):
        # После удаления перенаправляем на страницу профиля автора
        return reverse_lazy('blog:profile_detail', kwargs={'username': self.request.user.username})


class CommentDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Comment
    template_name = 'blog/comment_confirm_delete.html' # Создайте этот шаблон

    def get_object(self, _queryset=None):
        # Получаем комментарий по post_id и comment_id
        post_pk = self.kwargs.get('pk')
        comment_pk = self.kwargs.get('comment_pk')
        return get_object_or_404(Comment, pk=comment_pk, post__pk=post_pk)

    def test_func(self):
        # Проверка, что текущий пользователь - автор комментария
        comment = self.get_object()
        return self.request.user == comment.author
    
    def handle_no_permission(self):
        # Если пользователь не автор, перенаправляем на страницу поста
        comment = self.get_object()
        return redirect('blog:post_detail', pk=comment.post.pk)

    def get_success_url(self):
        # После удаления перенаправляем на страницу поста
        # self.object уже удален, но post_id мы можем получить
        return reverse_lazy('blog:post_detail', kwargs={'pk': self.kwargs.get('pk')})


class CommentUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Comment
    form_class = CommentForm
    template_name = 'blog/comment_edit.html' # Создадим простой шаблон для редактирования

    def get_object(self, _queryset=None):
        # Получаем комментарий по post_id и comment_id
        post_pk = self.kwargs.get('pk') # Это post_id
        comment_pk = self.kwargs.get('comment_pk') # Это comment_id
        return get_object_or_404(Comment, pk=comment_pk, post__pk=post_pk)

    def test_func(self):
        # Проверка, что текущий пользователь - автор комментария
        comment = self.get_object()
        return self.request.user == comment.author

    def handle_no_permission(self):
        # Если пользователь не автор, перенаправляем на страницу поста
        comment = self.get_object()
        return redirect('blog:post_detail', pk=comment.post.pk)

    def get_success_url(self):
        # После редактирования перенаправляем на страницу поста
        comment = self.get_object()
        return reverse_lazy('blog:post_detail', kwargs={'pk': comment.post.pk})

# Представление-заглушка для редактирования профиля
def edit_profile(request, username):
    # Здесь будет логика редактирования профиля
    return render(request, 'blog/edit_profile.html', {'username': username})
