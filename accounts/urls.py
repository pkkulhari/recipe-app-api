from django.urls import path

from . import views

app_name = "accounts"
urlpatterns = [
    path("create/", views.UserCreateView.as_view(), name="create"),
    path("token/", views.TokenCreateView.as_view(), name="token"),
    path("me/", views.ManageUserView.as_view(), name="me"),
]
