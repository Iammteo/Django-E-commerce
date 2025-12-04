# shop/views.py
from time import timezone
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import EmailMultiAlternatives
from django.shortcuts import get_object_or_404, render, redirect
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
import pyotp  # for 2FA l
from .forms import CustomUserCreationForm


User = get_user_model()


def home(request):
    return render(request, "shop/home.html")


def products_page(request):
    return render(request, "shop/products.html")


@login_required(login_url="signin")
def dashboard_page(request):
    return render(request, "shop/dashboard.html")



def signin_page(request):
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")

        user = authenticate(request, email=email, password=password)

        if user is None:
            messages.error(request, "Invalid email or password")
            return render(request, "shop/signin.html")

        if not user.is_email_verified:
            messages.error(request, "Please verify your email first. We just sent you a new code.")
            return redirect("resend_verification_code", user_id=user.id)

        # If 2FA enabled, go to 2FA step instead of logging in directly
        if user.is_2fa_enabled and user.totp_secret:
            request.session["2fa_user_id"] = user.id
            return redirect("two_factor_verify")

        # normal login
        login(request, user)
        return redirect("dashboards")

    return render(request, "shop/signin.html")



def register_page(request):
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, "Account created successfully. Please sign in.")
            return redirect("signin")
    else:
        form = CustomUserCreationForm()

    return render(request, "shop/register.html", {"form": form})




def verify_email_code(request, user_id):
    user = get_object_or_404(CustomUser, id=user_id)

    if request.method == "POST":
        code = request.POST.get("code", "").strip()

        if not user.email_verification_code or not user.email_verification_expires_at:
            messages.error(request, "No verification code found. Please request a new one.")
            return redirect("resend_verification_code", user_id=user.id)

        if timezone.now() > user.email_verification_expires_at:
            messages.error(request, "This code has expired. Please request a new one.")
            return redirect("resend_verification_code", user_id=user.id)

        if code != user.email_verification_code:
            messages.error(request, "Invalid verification code.")
            return render(request, "shop/verify_code.html", {"user": user})

        # success!
        user.is_email_verified = True
        user.email_verification_code = None
        user.email_verification_expires_at = None
        user.save()

        messages.success(request, "Email verified! You can now sign in.")
        return redirect("signin")

    return render(request, "shop/verify_code.html", {"user": user})


def resend_verification_code(request, user_id):
    user = get_object_or_404(CustomUser, id=user_id)

    # generate new code
    code = f"{random.randint(0, 999999):06d}"
    user.email_verification_code = code
    user.email_verification_expires_at = timezone.now() + timezone.timedelta(minutes=10)
    user.save()

    subject = "Your new TerraScope verification code"
    from_email = settings.DEFAULT_FROM_EMAIL
    to = [user.email]

    context = {
        "user": user,
        "code": code,
    }

    html_body = render(request, "emails/verify_code.html", context).content.decode("utf-8")

    email_message = EmailMultiAlternatives(
        subject=subject,
        body=f"Your new verification code is: {code}",
        from_email=from_email,
        to=to,
    )
    email_message.attach_alternative(html_body, "text/html")
    email_message.send()

    messages.success(request, "We sent you a new verification code.")
    return redirect("verify_email_code", user_id=user.id)




def password_reset_request(request):
    if request.method == "POST":
        email = request.POST.get("email")
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            messages.error(request, "We couldn't find an account with that email.")
            return redirect("password_reset")

        uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)
        reset_url = request.build_absolute_uri(
            reverse("password_reset_confirm", kwargs={"uidb64": uidb64, "token": token})
        )

        context = {"user": user, "reset_url": reset_url}
        html_body = render_to_string("emails/password_reset.html", context)

        email_message = EmailMultiAlternatives(
            subject="Reset your TerraScope password",
            body="Use the link to reset your password.",
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[user.email],
        )
        email_message.attach_alternative(html_body, "text/html")
        email_message.send()

        messages.success(request, "We emailed you a password reset link.")
        return redirect("signin")

    return render(request, "shop/password_reset_form.html")  # make this page


def password_reset_confirm(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is None or not default_token_generator.check_token(user, token):
        messages.error(request, "This password reset link is invalid or expired.")
        return redirect("password_reset")

    if request.method == "POST":
        password1 = request.POST.get("password1")
        password2 = request.POST.get("password2")

        if password1 != password2:
            messages.error(request, "Passwords don't match.")
        else:
            user.set_password(password1)
            user.save()
            messages.success(request, "Password updated! You can now sign in.")
            return redirect("signin")

    return render(request, "shop/password_reset_confirm.html", {"uidb64": uidb64, "token": token})


@login_required(login_url="signin")
def setup_2fa(request):
    user = request.user

    if request.method == "POST":
        code = request.POST.get("code", "").strip()

        if not user.totp_secret:
            messages.error(request, "Something went wrong. Refresh the page to get a new QR code.")
            return redirect("setup_2fa")

        totp = pyotp.TOTP(user.totp_secret)
        if totp.verify(code):
            user.is_2fa_enabled = True
            user.save()
            messages.success(request, "2FA enabled successfully 🎉")
            return redirect("dashboards")
        else:
            messages.error(request, "Invalid code. Try again.")

    # GET – show QR code / secret
    if not user.totp_secret:
        user.totp_secret = pyotp.random_base32()
        user.save()

    totp = pyotp.TOTP(user.totp_secret)
    otp_auth_url = totp.provisioning_uri(name=user.email, issuer_name="TerraScope")

    # you can generate a QR image and show it in template, or just show the URL
    context = {
        "otp_auth_url": otp_auth_url,
        "secret": user.totp_secret,
    }
    return render(request, "shop/setup_2fa.html", context)


def two_factor_verify(request):
    user_id = request.session.get("2fa_user_id")
    if not user_id:
        return redirect("signin")

    user = get_object_or_404(CustomUser, id=user_id)

    if request.method == "POST":
        code = request.POST.get("code", "").strip()
        totp = pyotp.TOTP(user.totp_secret)

        if totp.verify(code):
            # success
            login(request, user)
            request.session.pop("2fa_user_id", None)
            messages.success(request, "Logged in with 2FA ✅")
            return redirect("dashboards")
        else:
            messages.error(request, "Invalid 2FA code.")

    return render(request, "shop/two_factor_verify.html")



def logout_user(request):
    logout(request)
    return redirect("signin")
