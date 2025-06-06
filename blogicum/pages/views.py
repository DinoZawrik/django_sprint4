# blogicum/pages/views.py
from django.shortcuts import render
from django.views.generic import TemplateView


class AboutView(TemplateView):
    template_name = "pages/about.html"


class RulesView(TemplateView):
    template_name = "pages/rules.html"


class AuthorView(TemplateView):
    template_name = "pages/author.html"


class TechView(TemplateView):
    template_name = "pages/tech.html"


def page_not_found(request, exception):
    return render(request, "pages/404.html", status=404)


def csrf_failure(request, reason=""):
    return render(request, "pages/403csrf.html", status=403)


def server_error(request, exception=None):
    return render(request, "pages/500.html", status=500)
