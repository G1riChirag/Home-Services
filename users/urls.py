from django.urls import path
from .views import *

app_name = "users"

urlpatterns = [
    path("register/", RegisterView.as_view(), name="register"),
    path("login/", LoginWith2FAView.as_view(), name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("me/delete/", DeleteAccountView.as_view(), name="delete-account"),  # <-- NEW
]
