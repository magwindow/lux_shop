from django.contrib import admin

from .models import Product, Category, Gallery


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('title', 'parent')
    prepopulated_fields = {'slug': ('title',)}


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('pk', 'title', 'category', 'quantity', 'price', 'created_at', 'size', 'color')
    list_editable = ('price', 'quantity', 'size', 'color')
    prepopulated_fields = {'slug': ('title',)}
    list_filter = ('title', 'price')
    list_display_links = ('pk', 'title')


admin.site.register(Gallery)
