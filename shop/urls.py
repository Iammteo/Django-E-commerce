
# shop/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('products/', views.products_page, name='products'),
    path('dashboards/', views.dashboard_page, name='dashboards'),

    path('auth/login/', views.signin_page, name='signin'),
    path('auth/register/', views.register_page, name='register'),

    # email verification
    path('auth/verify-code/<int:user_id>/', views.verify_email_code, name='verify_email_code'),
    path('auth/resend-code/<int:user_id>/', views.resend_verification_code, name='resend_verification_code'),

    # 2FA
    path('auth/setup-2fa/', views.setup_2fa, name='setup_2fa'),
    path('auth/2fa-verify/', views.two_factor_verify, name='two_factor_verify'),

    # password reset
    path(
        "auth/password-reset/",
        views.password_reset_request,
        name="password_reset",
    ),
    path(
        "auth/password-reset/<uidb64>/<token>/",
        views.password_reset_confirm,
        name="password_reset_confirm",
    ),

]




# from django.urls import path
# from . import views

# urlpatterns = [
#     path("", views.home, name="home"),
#     path("products/", views.products_page, name="products"),
#     path("dashboards/", views.dashboard_page, name="dashboards"),

#     # auth
#     path("auth/login/", views.signin_page, name="signin"),
#     path("auth/register/", views.register_page, name="register"),
#     path("auth/logout/", views.logout_user, name="logout"),

#     # email verification
#     path(
#         "auth/verify/<uidb64>/<token>/",
#         views.verify_email,
#         name="verify_email",
#     ),

#     # password reset
#     path(
#         "auth/password-reset/",
#         views.password_reset_request,
#         name="password_reset",
#     ),
#     path(
#         "auth/password-reset/<uidb64>/<token>/",
#         views.password_reset_confirm,
#         name="password_reset_confirm",
#     ),
# ]


