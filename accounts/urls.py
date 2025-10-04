from django.contrib import admin
from django.urls import path,include
from . import views

urlpatterns = [
    path("quiz/", views.quiz, name="quiz"),
    path("register/", views.register, name="register"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("profile/", views.profile, name="profile"),
]
