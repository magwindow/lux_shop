from django.shortcuts import render, redirect
from django.views.generic import ListView, DetailView

from .models import Category, Product


class Index(ListView):
    """Главная страница"""
    model = Product
    context_object_name = 'categories'
    extra_context = {'title': 'Главная страница'}
    template_name = 'shop/index.html'

    def get_queryset(self):
        """Вывод родительской категории"""
        categories = Category.objects.filter(parent=None)
        return categories
