import logging

from django.contrib.auth import login
from django.contrib.auth.views import LoginView, LogoutView
from django.shortcuts import redirect, render

from .forms import SignUpForm

logger = logging.getLogger("chat")


def frontpage(request):
    return render(request, "core/frontpage.html")


def signup(request):
    if request.method == "POST":
        form = SignUpForm(request.POST)

        if form.is_valid():
            user = form.save()

            login(request, user)
            logger.info(f"User {user.username} has registered to ChatApp")

            return redirect("frontpage")
    else:
        form = SignUpForm()

    return render(request, "core/signup.html", {"form": form})


class CustomLoginView(LoginView):
    def form_valid(self, form):
        logger.info(f"User {form.get_user().username} has logged into ChatApp")
        return super().form_valid(form)


class CustomLogoutView(LogoutView):
    def dispatch(self, request, *args, **kwargs):
        logger.info(f"User {request.user} has logged out of ChatApp")
        return super().dispatch(request, *args, **kwargs)
