"""blogicum URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import include, path
from django.conf import settings  # Для медиа-файлов
from django.conf.urls.static import static  # Для медиа-файлов
from django.views.generic import CreateView
from django.urls import reverse_lazy
from blog.forms import CreationForm

urlpatterns = [
    path("admin/", admin.site.urls),
    path("pages/", include("pages.urls", namespace="pages")),
    path("", include("blog.urls", namespace="blog")),
    path("auth/", include("django.contrib.auth.urls")),
    path(
        "auth/registration/register/",
        CreateView.as_view(
            form_class=CreationForm,
            success_url=reverse_lazy("blog:index"),
            template_name="registration/registration_form.html",
        ),
        name="register",
    ),  # Используем CreateView для регистрации
]

# Для отдачи медиа-файлов в режиме разработки
if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL, document_root=settings.MEDIA_ROOT
    )

handler500 = "blog.views.server_error"

handler404 = "pages.views.page_not_found"
handler403 = "pages.views.csrf_failure"
