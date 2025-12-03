
from django.urls import path
from .views import home, products_page

urlpatterns = [
    path('', home, name='home'),
    path('products/', products_page, name='products'),
]
