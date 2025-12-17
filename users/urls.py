from django.urls import path
from .views import SigninView, RefreshView, SignoutView, MeView, RegisterView

urlpatterns = [
    path("register/", RegisterView.as_view()),
    path("token/", SigninView.as_view()),
    path("token/refresh/", RefreshView.as_view()),
    path("logout/", SignoutView.as_view()),
    path("me/", MeView.as_view()),
]
