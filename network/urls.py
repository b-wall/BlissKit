
from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("register/", views.register, name="register"),
    path("posts/", views.allposts, name="allposts"),
    path("user/<int:uid>/", views.userprofile, name="userprofile"),
    path("following/", views.following, name="following"),

    # API Routes
    path("follow/<int:uid>/", views.follow, name="follow"),
    path("edit/<int:post_id>/", views.edit, name="edit"),
    path("like/<int:post_id>/", views.like_handle, name="like-handle"),
    path("likes/", views.like_display, name="like-display"),
]
