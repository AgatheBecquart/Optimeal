from django.contrib import admin
from django.urls import path
from django.contrib import admin
from blog.views import home, predict_view, predictions_view
from authentication.views import (
    SignUpView,
    CustomLoginView,
    custom_logout,
    ProfileUpdateView,
    CustomPasswordChangeView,
    CustomPasswordResetView,
    CustomPasswordResetConfirmView,
)


urlpatterns = [
    path("admin/", admin.site.urls),
    path("", home, name="home"),
    path("signup/", SignUpView.as_view(), name="signup"),
    path("login/", CustomLoginView.as_view(), name="login"),
    path("logout/", custom_logout, name="logout"),
    path("profile/", ProfileUpdateView.as_view(), name="profile"),
    path(
        "password_change/", CustomPasswordChangeView.as_view(), name="password_change"
    ),
    path("password_reset/", CustomPasswordResetView.as_view(), name="password_reset"),
    path(
        "password_reset_confirm/<uidb64>/<token>/",
        CustomPasswordResetConfirmView.as_view(),
        name="password_reset_confirm",
    ),
    path("predict/", predict_view, name="predict_view"),
    path("predictions/", predictions_view, name="predictions"),
]
