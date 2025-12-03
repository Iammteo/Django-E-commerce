# from django.contrib import admin
# from .models import Product


from .models import Order
from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin

from django.contrib import admin
from .models import Product

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display  = ("name", "category", "price", "active", "created_at")
    list_filter   = ("category", "active")
    search_fields = ("name", "category")


# optional: unregister default
admin.site.unregister(User)

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ("username", "email", "is_staff", "is_active", "date_joined")
    list_filter = ("is_staff", "is_superuser", "is_active")
    search_fields = ("username", "email")



@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display  = ("id", "user", "product", "status", "total_price", "created_at")
    list_filter   = ("status", "created_at")
    search_fields = ("user__username", "product__name")
    date_hierarchy = "created_at"

