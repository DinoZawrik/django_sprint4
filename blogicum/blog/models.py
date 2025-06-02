from django.db import models
from django.contrib.auth import get_user_model

# Получаем встроенную модель User
User = get_user_model()


class Category(models.Model):
    title = models.CharField(
        "Заголовок", max_length=256, help_text="Макс длина — 256 символов."
    )
    description = models.TextField("Описание")
    slug = models.SlugField(
        "Идентификатор",
        unique=True,
        help_text=(
            "Идентификатор страницы для URL; "
            "разрешены символы латиницы, цифры, дефис и подчёркивание."
        ),
    )
    is_published = models.BooleanField(
        "Опубликовано",
        default=True,
        help_text="Снимите галочку, чтобы скрыть публикацию.",
    )
    created_at = models.DateTimeField("Добавлено", auto_now_add=True)

    class Meta:
        verbose_name = "категория"
        verbose_name_plural = "Категории"
        ordering = ["title"]  # Для удобства, можно удалить

    def __str__(self):
        return self.title


class Location(models.Model):
    name = models.CharField(
        "Название места", max_length=256, help_text="256 символов."
    )
    is_published = models.BooleanField(
        "Опубликовано",
        default=True,
        help_text="Снимите галочку, чтобы скрыть публикацию.",
    )
    created_at = models.DateTimeField("Добавлено", auto_now_add=True)

    class Meta:
        verbose_name = "местоположение"
        verbose_name_plural = "Местоположения"
        ordering = ["name"]  # Для удобства, можно удалить

    def __str__(self):
        return self.name


class Post(models.Model):
    title = models.CharField("Заголовок", max_length=256)
    text = models.TextField("Текст")
    pub_date = models.DateTimeField(
        verbose_name='Дата и время публикации',
        help_text='Если установить дату и время в будущем — '
                  'можно делать отложенные публикации.'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="posts",
        verbose_name="Автор публикации",
    )
    location = models.ForeignKey(
        Location,
        on_delete=models.SET_NULL,
        null=True,  # Разрешает NULL в базе данных
        blank=True,  # Разрешает не заполнять поле в формах/админке
        related_name="posts",
        verbose_name="Местоположение",
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        blank=False,
        related_name="posts",
        verbose_name="Категория",
    )
    is_published = models.BooleanField(
        "Опубликовано",
        default=True,
        help_text="Снимите галочку, чтобы скрыть публикацию.",
    )
    created_at = models.DateTimeField("Добавлено", auto_now_add=True)

    class Meta:
        verbose_name = "публикация"
        verbose_name_plural = "Публикации"
        ordering = [
            "-pub_date"
        ]  # По умолчанию сортируем по дате публикации (от новых к старым)

    def __str__(self):
        return self.title
