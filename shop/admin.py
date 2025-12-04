from django.contrib import admin
from .models import Product, Order

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("name", "category", "price", "active", "created_at")
    list_filter = ("category", "active")
    search_fields = ("name", "category")

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "product", "status", "total_price", "created_at")
    list_filter = ("status", "created_at")
    search_fields = ("user__username", "product__name")
    date_hierarchy = "created_at"
