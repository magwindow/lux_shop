from django.contrib import admin
from django.utils.safestring import mark_safe

from .models import *


class GalleryInline(admin.TabularInline):
    """Отображение галереи картинок"""
    fk_name = 'product'
    model = Gallery
    extra = 1


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    """Отображение категории товаров"""
    list_display = ('title', 'parent', 'get_products_count')
    prepopulated_fields = {'slug': ('title',)}

    def get_products_count(self, obj):
        """Отображение количество товаров каждой категории"""
        if obj.products:
            return str(len(obj.products.all()))
        else:
            return '0'

    get_products_count.short_description = 'Количество товаров'


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    """Отображение товаров"""
    list_display = ('pk', 'title', 'category', 'quantity', 'price', 'created_at', 'size', 'color', 'get_photo')
    list_editable = ('price', 'quantity', 'size', 'color')
    prepopulated_fields = {'slug': ('title',)}
    list_filter = ('title', 'price')
    list_display_links = ('pk', 'title')
    inlines = (GalleryInline,)

    def get_photo(self, obj):
        """Отображение миниатюры"""
        if obj.images.all():
            return mark_safe(f'<img src="{obj.images.all()[0].image.url}" width="75">')
        else:
            return '-'

    get_photo.short_description = 'Миниатюра'


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    """Отображение отзывов"""
    list_display = ('pk', 'author', 'created_at')


@admin.register(Mail)
class MailAdmin(admin.ModelAdmin):
    """Почтовые подписки"""
    list_display = ('pk', 'mail', 'user')


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    """Корзина"""
    list_display = ('customer', 'created_at', 'is_completed', 'shipping')
    list_filter = ('customer', 'is_completed')


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    """Заказчики"""
    list_display = ('user', 'first_name', 'last_name', 'email')
    list_filter = ('user',)


@admin.register(OrderProduct)
class OrderProductAdmin(admin.ModelAdmin):
    """Товары в заказах"""
    list_display = ('product', 'order', 'quantity', 'added_at')
    list_filter = ('product',)


@admin.register(ShippingAddress)
class ShippingAddressAdmin(admin.ModelAdmin):
    """Адреса доставки"""
    list_display = ('customer', 'city', 'state')
    list_filter = ('customer',)


admin.site.register(Gallery)
