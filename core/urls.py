from django.urls import path

from . import views

urlpatterns = [
    path("", views.frontpage, name="frontpage"),
    path("signup/", views.signup, name="signup"),
    path(
        "login/",
        views.CustomLoginView.as_view(template_name="core/login.html"),
        name="login",
    ),
    path("logout/", views.CustomLogoutView.as_view(), name="logout"),
]
