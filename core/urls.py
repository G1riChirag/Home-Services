# core/urls.py

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

from users.views import LoginWith2FAView
from .views import HomeView

urlpatterns = [
    # Authentication routes
    path("accounts/login/", LoginWith2FAView.as_view(), name="login"),
    path("accounts/", include("django.contrib.auth.urls")),

    # Admin panel
    path("admin/", admin.site.urls),

    # App routes
    path("", HomeView.as_view(), name="home"),
    path("", include(("users.urls", "users"), namespace="users")),
    path("", include("profiles.urls")),
    path("", include("catalog.urls")),
    path("", include("bookings.urls")),
    path("", include("bookings.urls")),
    path("", include(("payments.urls", "payments"), namespace="payments")), 
]

# --- Serve media files (for vaccination proofs, uploaded images, etc.) ---
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
