from django import template
from django.template.defaulttags import register as range_register

from shop.models import Category, FavoriteProducts

register = template.Library()


@register.simple_tag()
def get_subcategories(category):
    """Подкатегории товаров"""
    return Category.objects.filter(parent=category)


@register.simple_tag()
def get_sorted():
    """Сортировка товаров по цене, цвету, размеру"""
    sorters = [
        {
            'title': 'Цена',
            'sorters': [
                ('price', 'По возрастанию'),
                ('-price', 'По убыванию')
            ]
        },
        {
            'title': 'Цвет',
            'sorters': [
                ('color', 'от А до Я'),
                ('-color', 'от Я до А')
            ]
        },
        {
            'title': 'Размер',
            'sorters': [
                ('size', 'По возрастанию'),
                ('-size', 'По убыванию')
            ]
        }
    ]
    return sorters


@range_register.filter
def get_positive_range(value):
    """Отображение кол-во закрашенных звезд"""
    return range(int(value))


@range_register.filter
def get_negative_range(value):
    """Отображение кол-во пустых звезд"""
    return range(5 - int(value))


@register.simple_tag()
def get_favorite_products(user):
    """Вывод избранных товаров на страницу"""
    fav = FavoriteProducts.objects.filter(user=user)
    products = [i.product for i in fav]
    return products

