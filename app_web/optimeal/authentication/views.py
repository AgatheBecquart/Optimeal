from django.contrib.auth import login, logout
from django.contrib.auth.views import (
    LoginView,
    LogoutView,
    PasswordChangeView,
    PasswordResetView,
    PasswordResetConfirmView,
)
from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse_lazy
from django.views.generic import CreateView, UpdateView
from .forms import CustomUserCreationForm, CustomUserChangeForm
from .models import CustomUser
from django.contrib import messages
from django.shortcuts import redirect
from django.utils.decorators import method_decorator
from django.views.decorators.http import require_http_methods


class SignUpView(SuccessMessageMixin, CreateView):
    form_class = CustomUserCreationForm
    success_url = reverse_lazy("login")
    template_name = "authentication/signup.html"
    success_message = (
        "Votre compte a été créé avec succès. Vous pouvez maintenant vous connecter."
    )


class CustomLoginView(SuccessMessageMixin, LoginView):
    template_name = "authentication/login.html"
    success_message = "Vous êtes maintenant connecté."


def custom_logout(request):
    logout(request)
    messages.success(request, "Vous avez été déconnecté avec succès.")
    return redirect(
        "login"
    )  # ou 'home' si vous préférez rediriger vers la page d'accueil


class ProfileUpdateView(SuccessMessageMixin, UpdateView):
    model = CustomUser
    form_class = CustomUserChangeForm
    template_name = "authentication/profile.html"
    success_url = reverse_lazy("profile")
    success_message = "Votre profil a été mis à jour avec succès."

    def get_object(self):
        return self.request.user


class CustomPasswordChangeView(SuccessMessageMixin, PasswordChangeView):
    template_name = "authentication/password_change.html"
    success_url = reverse_lazy("profile")
    success_message = "Votre mot de passe a été changé avec succès."


class CustomPasswordResetView(SuccessMessageMixin, PasswordResetView):
    template_name = "authentication/password_reset.html"
    email_template_name = "authentication/password_reset_email.html"
    subject_template_name = "authentication/password_reset_subject.txt"
    success_url = reverse_lazy("login")
    success_message = "Un email a été envoyé avec les instructions pour réinitialiser votre mot de passe."


class CustomPasswordResetConfirmView(SuccessMessageMixin, PasswordResetConfirmView):
    template_name = "authentication/password_reset_confirm.html"
    success_url = reverse_lazy("login")
    success_message = "Votre mot de passe a été réinitialisé avec succès. Vous pouvez maintenant vous connecter."
