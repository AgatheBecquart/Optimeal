from django.contrib import admin
from django.contrib.auth.views import (
    LoginView, LogoutView, PasswordChangeView, PasswordChangeDoneView)
from django.urls import path
from django.contrib import admin
from authentication.views import signup_view, update_employee_view, login_view
from blog.views import home, predict_view

urlpatterns = [
    path('admin/', admin.site.urls),
    path('signup/', signup_view, name='signup'),
    path('login/', login_view, name='login'),
    path('update_employee/', update_employee_view, name='update_employee'),
    path('', home, name='home'),
    path('predict/', predict_view, name='predict_view'),
]
