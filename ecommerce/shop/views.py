from django.shortcuts import render

def home(request):
    return render(request, 'shop/home.html')

def products_page(request):
    return render(request, 'shop/products.html')
