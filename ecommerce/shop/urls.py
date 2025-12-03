
from django.urls import path
from .views import home, products_page, dashboard_page, register_page, signin_page

urlpatterns = [
    path('', home, name='home'),
    path('products/', products_page, name='products'),
    path('dashboards/', dashboard_page, name='dashboards'),
    path('auth/login/', signin_page, name='signin'),
    path('auth/register/', register_page, name='register'),
]

