from django.urls import path
from . import views

urlpatterns = [
    path("", views.fundme_list, name="fundme_list"),
    path("<int:pk>/", views.fundme_detail, name="fundme_detail"),
    path("create/", views.fundme_create, name="fundme_create"),
    path("<int:pk>/edit/", views.fundme_update, name="fundme_update"),
    path("<int:pk>/delete/", views.fundme_delete, name="fundme_delete"),
]
