from django.shortcuts import get_object_or_404, render
from django.utils import timezone  # Работа с датой и временем
from django.http import Http404  # Генерация ошибки 404
from .models import Post, Category, Comment  # Импорт моделей
from django.urls import reverse_lazy
from django.views.generic import CreateView, UpdateView, DeleteView # Для CBV
from django.contrib.auth import get_user_model
from .forms import PostForm, CommentForm, ProfileEditForm # Импортируем формы
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin # Для CBV и проверки прав
from django.shortcuts import redirect # Для ручных редиреков
from django.db.models import Count, Q
# from django.db.models.expressions import OrderBy # Импортируем OrderBy
from django.core.paginator import Paginator # Импортируем Paginator


User = get_user_model() # В начале файла


def index(request):
    # Получаем все опубликованные посты из опубликованных
    # категорий, дата публикации которых не позже текущего времени.
    # select_related() используется для оптимизации запросов
    post_list = ( # Изменяем имя переменной на post_list
        Post.objects.select_related("category", "author", "location")
        .filter(
            Q(pub_date__lte=timezone.now()) | Q(pub_date__isnull=True), # Дата публикации не позже текущего или пустая
            is_published=True,  # Пост опубликован
            category__is_published=True,  # Категория поста опубликована
            # (исключает посты с category=None)
        )
        .annotate(comment_count=Count('comments')) # Добавляем количество комментариев
        .order_by("-pub_date")
    )  # Сортируем по дате публикации по убыванию

    # Создаем объект Paginator с 10 постами на странице
    paginator = Paginator(post_list, 10)

    # Получаем номер текущей страницы из GET-параметра 'page'
    page_number = request.GET.get('page')

    # Получаем объект Page для текущей страницы
    page_obj = paginator.get_page(page_number)

    context = {
        "page_obj": page_obj, # Передаем объект Page в контекст
    }
    return render(request, "blog/index.html", context)


def category_posts(request, slug):
    # Получаем объект категории по slug.
    # Если категория не найдена или не опубликована, возвращаем 404.
    category = get_object_or_404(Category, slug=slug, is_published=True)

    # Получаем посты выбранной категории, опубликованные,
    # и дата публикации которых не позже текущего времени.
    post_list = ( # Изменяем имя переменной на post_list
        Post.objects.select_related("author", "location")
        .filter(
            Q(pub_date__lte=timezone.now()) | Q(pub_date__isnull=True), # Дата публикации не позже текущего или пустая
            category=category,  # Посты принадлежат данной категории
            is_published=True,  # Пост опубликован
        )
        .annotate(comment_count=Count('comments')) # Добавляем количество комментариев
        .order_by("-pub_date")
    )

    # Создаем объект Paginator с 10 постами на странице
    paginator = Paginator(post_list, 10)

    # Получаем номер текущей страницы из GET-параметра 'page'
    page_number = request.GET.get('page')

    # Получаем объект Page для текущей страницы
    page_obj = paginator.get_page(page_number)

    context = {
        "category": category,
        "page_obj": page_obj, # Передаем объект Page в контекст
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
    # Проверяем условия для возврата ошибки 404:
    # 1. Дата публикации позже текущего времени (если дата указана)
    # 2. Пост не опубликован
    # 3. Категория поста отсутствует ИЛИ категория поста не опубликована
    # Проверяем условия для возврата ошибки 404:
    # Если текущий пользователь - автор поста, показываем пост независимо от статуса публикации и даты.
    # Иначе - применяем фильтры.
    if request.user != post.author:
        if (
            (post.pub_date is not None and post.pub_date > timezone.now()) # Дата публикации позже текущего времени (если дата указана)
            or not post.is_published # Пост не опубликован
            or (post.category is None or not post.category.is_published) # Категория поста отсутствует ИЛИ категория поста не опубликована
        ):
            raise Http404("Публикация не найдена или не опубликована.")


    comment_form = CommentForm()
    context = {
        'post': post,
        'form': comment_form, # Передаем форму комментария
    }
    return render(request, 'blog/detail.html', context)

def profile_detail(request, username):
    # Получаем объект пользователя по username.
    # Если пользователь не найден, возвращаем 404.
    profile = get_object_or_404(User, username=username)

    # Получаем посты автора, опубликованные,
    # и дата публикации которых не позже текущего времени.
    # Получаем посты автора.
    # Если текущий пользователь - автор профиля, показываем все посты.
    # Иначе - только опубликованные, не отложенные и из опубликованных категорий.
    if request.user == profile:
        post_list = (
            profile.posts.select_related("category", "location")
            .annotate(comment_count=Count('comments')) # Добавляем количество комментариев
            .order_by('-pub_date') # Сортируем по дате публикации по убыванию
        )
    else:
        post_list = (
            profile.posts.select_related("category", "location")
            .filter(
                is_published=True,  # Пост опубликован
                pub_date__lte=timezone.now(),  # Дата публикации не позже текущего
                category__is_published=True,  # Категория поста опубликована
            )
            .annotate(comment_count=Count('comments')) # Добавляем количество комментариев
            .order_by('-pub_date') # Сортируем по дате публикации по убыванию
        )

    # Создаем объект Paginator с 10 постами на странице
    paginator = Paginator(post_list, 10)

    # Получаем номер текущей страницы из GET-параметра 'page'
    page_number = request.GET.get('page')

    # Получаем объект Page для текущей страницы
    page_obj = paginator.get_page(page_number)

    context = {
        "profile": profile,
        "page_obj": page_obj, # Передаем объект Page в контекст
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
        'form': form, # Передаем форму комментария с ошибками
    }
    return render(request, 'blog/detail.html', context) # Рендерим обратно detail.html с формой и ошибками

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

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Если 'form' есть в контексте, удаляем его
        if 'form' in context:
            del context['form']
        return context

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
@login_required # Добавляем декоратор для проверки авторизации
def edit_profile(request, username):
    user_to_edit = get_object_or_404(User, username=username)

    # Проверяем, является ли текущий пользователь владельцем профиля
    if request.user != user_to_edit:
        return redirect('blog:profile_detail', username=username) # Перенаправляем, если не владелец

    if request.method == 'POST':
        form = ProfileEditForm(request.POST, instance=user_to_edit)
        if form.is_valid():
            form.save()
            return redirect('blog:profile_detail', username=username) # Перенаправляем на страницу профиля после сохранения
    else:
        form = ProfileEditForm(instance=user_to_edit) # Заполняем форму данными пользователя

    context = {
        'form': form,
        'profile': user_to_edit, # Передаем объект пользователя в контекст
    }
    return render(request, 'blog/edit_profile.html', context)

def server_error(request):
    return render(request, 'pages/500.html', status=500)
