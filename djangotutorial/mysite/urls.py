from django.contrib import admin
from django.urls import include, path
from django.contrib.auth import views as auth_views
from polls import views as polls_views


urlpatterns = [
    path("polls/", include("polls.urls")),
    path("admin/", admin.site.urls),
    path("login/", auth_views.LoginView.as_view(), name="login"),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
    path("register/", polls_views.register, name="register"),

]