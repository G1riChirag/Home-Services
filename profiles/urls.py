from django.urls import path
from .views import (
    ProfileView,
    ProfileUpdateView,
    Profile2FAEnableView,
    Profile2FADisableView,
    ReportPositiveView,
    AcknowledgeAlertView,
)

urlpatterns = [
    path("profile/", ProfileView.as_view(), name="profile"),
    path("profile/edit/", ProfileUpdateView.as_view(), name="profile-edit"),

    path("me/profile/2fa/enable/", Profile2FAEnableView.as_view(), name="profile-2fa-enable"),
    path("me/profile/2fa/disable/", Profile2FADisableView.as_view(), name="profile-2fa-disable"),

    path("me/health/report-positive/", ReportPositiveView.as_view(), name="report-positive"),
    path("me/health/acknowledge-alerts/", AcknowledgeAlertView.as_view(), name="ack-alerts"),
]
