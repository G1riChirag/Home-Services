
from django.urls import path
from .views import ServiceListView, PackageListView, PackageDetailView

urlpatterns = [
    path("services/", ServiceListView.as_view(), name="services"),
    path("packages/", PackageListView.as_view(), name="packages"),
    path("packages/<int:pk>/", PackageDetailView.as_view(), name="package-detail"),
]
