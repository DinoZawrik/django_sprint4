from django.shortcuts import get_object_or_404, render
from django.utils import timezone  # Работа с датой и временем
from django.http import Http404  # Генерация ошибки 404
from .models import Post, Category, Comment  # Импорт моделей
from django.urls import reverse_lazy
from django.views.generic import CreateView, UpdateView, DeleteView  # Для CBV
from django.contrib.auth import get_user_model
from .forms import PostForm, CommentForm, ProfileEditForm  # Импортируем формы
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import (
    LoginRequiredMixin,
    UserPassesTestMixin,
)  # Для CBV и проверки прав
from django.shortcuts import redirect  # Для ручных редиреков
from django.db.models import Count, Q
from django.core.paginator import Paginator


User = get_user_model()


def get_published_posts(queryset):
    """
    Фильтрует посты по статусу публикации и дате.
    """
    return queryset.filter(
        Q(pub_date__lte=timezone.now()) | Q(pub_date__isnull=True),
        is_published=True,
        category__is_published=True,
    )


def get_posts_with_comments(queryset):
    """
    Аннотирует queryset постов количеством комментариев и сортирует.
    """
    return queryset.annotate(comment_count=Count("comments")).order_by("-pub_date")


def get_page_obj(request, post_list, posts_per_page=10):
    """
    Возвращает объект страницы пагинатора.
    """
    paginator = Paginator(post_list, posts_per_page)
    page_number = request.GET.get("page")
    return paginator.get_page(page_number)


def index(request):
    post_list = get_posts_with_comments(
        get_published_posts(Post.objects.select_related("category", "author", "location"))
    )
    page_obj = get_page_obj(request, post_list)
    context = {
        "page_obj": page_obj,
    }
    return render(request, "blog/index.html", context)


def category_posts(request, slug):
    category = get_object_or_404(Category, slug=slug, is_published=True)
    post_list = get_posts_with_comments(
        get_published_posts(
            Post.objects.select_related("author", "location").filter(category=category)
        )
    )
    page_obj = get_page_obj(request, post_list)
    context = {
        "category": category,
        "page_obj": page_obj,
    }
    return render(request, "blog/category.html", context)


def post_detail(request, post_id):
    post = get_object_or_404(
        Post.objects.select_related("category", "author", "location"), pk=post_id
    )

    if request.user != post.author:
        if (
            (post.pub_date is not None and post.pub_date > timezone.now())
            or not post.is_published
            or (post.category is None or not post.category.is_published)
        ):
            raise Http404("Публикация не найдена или не опубликована.")

    comment_form = CommentForm()
    context = {
        "post": post,
        "comment_form": comment_form,
    }
    return render(request, "blog/detail.html", context)


def profile_detail(request, username):
    profile = get_object_or_404(User, username=username)

    if request.user == profile:
        post_list = get_posts_with_comments(
            profile.posts.select_related("category", "location")
        )
    else:
        post_list = get_posts_with_comments(
            get_published_posts(profile.posts.select_related("category", "location"))
        )

    page_obj = get_page_obj(request, post_list)
    context = {
        "profile": profile,
        "page_obj": page_obj,
    }
    return render(request, "blog/profile.html", context)


class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    form_class = PostForm
    template_name = "blog/create.html"

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy(
            "blog:profile_detail",
            kwargs={"username": self.request.user.username},
        )


class PostUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Post
    form_class = PostForm
    template_name = "blog/create.html"
    pk_url_kwarg = "post_id"

    def test_func(self):
        post = self.get_object()
        return self.request.user == post.author

    def handle_no_permission(self):
        post = self.get_object()
        return redirect("blog:post_detail", post_id=post.pk)

    def get_success_url(self):
        return reverse_lazy(
            "blog:post_detail", kwargs={"post_id": self.get_object().pk}
        )


@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
        return redirect("blog:post_detail", post_id=post_id)
    context = {
        "post": post,
        "form": form,
    }
    return render(request, "blog/detail.html", context)


class PostDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Post
    template_name = "blog/post_confirm_delete.html"
    pk_url_kwarg = "post_id"

    def test_func(self):
        post = self.get_object()
        return self.request.user == post.author

    def handle_no_permission(self):
        post = self.get_object()
        return redirect("blog:post_detail", post_id=post.pk)

    def get_success_url(self):
        return reverse_lazy(
            "blog:profile_detail",
            kwargs={"username": self.request.user.username},
        )


class CommentDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Comment
    template_name = "blog/comment_confirm_delete.html"
    pk_url_kwarg = "comment_id"

    def get_object(self, _queryset=None):
        post_id = self.kwargs.get("post_id")
        comment_id = self.kwargs.get("comment_id")
        return get_object_or_404(Comment, pk=comment_id, post__pk=post_id)

    def test_func(self):
        comment = self.get_object()
        return self.request.user == comment.author

    def handle_no_permission(self):
        comment = self.get_object()
        return redirect("blog:post_detail", post_id=comment.post.pk)

    def get_success_url(self):
        return reverse_lazy(
            "blog:post_detail", kwargs={"post_id": self.kwargs.get("post_id")}
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if "form" in context:
            del context["form"]
        return context


class CommentUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Comment
    form_class = CommentForm
    template_name = "blog/comment_edit.html"
    pk_url_kwarg = "comment_id"

    def get_object(self, _queryset=None):
        post_id = self.kwargs.get("post_id")
        comment_id = self.kwargs.get("comment_id")
        return get_object_or_404(Comment, pk=comment_id, post__pk=post_id)

    def test_func(self):
        comment = self.get_object()
        return self.request.user == comment.author

    def handle_no_permission(self):
        comment = self.get_object()
        return redirect("blog:post_detail", post_id=comment.post.pk)

    def get_success_url(self):
        comment = self.get_object()
        return reverse_lazy(
            "blog:post_detail", kwargs={"post_id": comment.post.pk}
        )


@login_required
def edit_profile(request, username):
    user_to_edit = get_object_or_404(User, username=username)

    if request.user != user_to_edit:
        return redirect("blog:profile_detail", username=username)

    if request.method == "POST":
        form = ProfileEditForm(request.POST, instance=user_to_edit)
        if form.is_valid():
            form.save()
            return redirect("blog:profile_detail", username=username)
    else:
        form = ProfileEditForm(instance=user_to_edit)

    context = {
        "form": form,
        "profile": user_to_edit,
    }
    return render(request, "blog/edit_profile.html", context)


def server_error(request):
    return render(request, "pages/500.html", status=500)
