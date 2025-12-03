
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required

def home(request):
    return render(request, 'shop/home.html')

def products_page(request):
    return render(request, 'shop/products.html')

@login_required(login_url="signin")
def dashboard_page(request):
    return render(request, 'shop/dashboard.html')


def signin_page(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect("dashboards")
   # after login, go to dashboard
        else:
            messages.error(request, "Invalid username or password")

    return render(request, "shop/signin.html")


def register_page(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()      # create the user
            login(request, user)    # optionally log them in straight away
            messages.success(request, "Account created successfully!")
            return redirect("dashboards")

        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = UserCreationForm()

    return render(request, "shop/register.html", {"form": form})


def logout_user(request):
    logout(request)
    return redirect("signin")

