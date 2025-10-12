from django.urls import path
from . import views

app_name = "posts"

urlpatterns = [
    path("feed/", views.feed, name="feed"),
    path("create/", views.create_post, name="create_post"),
    path("post/<int:post_id>/", views.post_detail, name="detail"),
    path("post/<int:post_id>/comment/", views.add_comment, name="add_comment"),
    path("post/<int:post_id>/like/", views.toggle_like, name="toggle_like"),
    path("profile/<int:profile_id>/follow/", views.toggle_follow, name="toggle_follow"),
    path("profile/<int:profile_id>/", views.profile_posts, name="profile_posts"),
path("post/<int:post_id>/edit/", views.edit_post, name="edit_post"),
path("post/<int:post_id>/delete/", views.delete_post, name="delete_post"),
path("emergency/", views.emergency_feed, name="emergency_feed"),

]