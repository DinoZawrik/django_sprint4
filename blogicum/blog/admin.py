from django.contrib import admin
from .models import Post, Category, Location, Comment  # Импорт Comment


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "pub_date",
        "author",
        "category",
        "location",
        "image",
        "is_published",
        "created_at",
    )
    list_filter = (
        "is_published",
        "pub_date",
        "category",
        "author",
        "location",
    )
    search_fields = (
        "title",
        "text",
    )
    empty_value_display = "-не указано-"  # Отображение полей с NULL


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "slug",
        "is_published",
        "created_at",
    )
    list_filter = ("is_published",)
    search_fields = (
        "title",
        "description",
    )
    prepopulated_fields = {"slug": ("title",)}  # Автозаполнение slug из title
    empty_value_display = "-не указано-"


@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "is_published",
        "created_at",
    )
    list_filter = ("is_published",)
    search_fields = ("name",)
    empty_value_display = "-не указано-"


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = (
        "text",
        "post",
        "author",
        "created_at",
    )
    list_filter = ("created_at", "author")
    search_fields = ("text", "post__title", "author__username")
