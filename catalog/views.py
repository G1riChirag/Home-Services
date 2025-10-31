
from django.views.generic import ListView, DetailView
from django.urls import reverse
from .models import Service, ServicePackage
from utils.mixins import BreadcrumbsMixin


class ServiceListView(BreadcrumbsMixin, ListView):
    template_name = "catalog/services_list.html"
    model = Service
    context_object_name = "services"

    def get_breadcrumbs(self):
        return [
            {"label": "Home", "url": reverse("home")},
            {"label": "Services"},
        ]

class PackageListView(BreadcrumbsMixin, ListView):
    template_name = "catalog/packages_list.html"
    model = ServicePackage
    context_object_name = "packages"

    def get_breadcrumbs(self):
        return [
            {"label": "Home", "url": reverse("home")},
            {"label": "Packages"},
        ]

class PackageDetailView(BreadcrumbsMixin, DetailView):
    template_name = "catalog/package_detail.html"
    model = ServicePackage
    context_object_name = "package"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        b = self.object
        ctx["breadcrumbs"] = [
            {"label": "Home", "url": reverse("home")},
            {"label": "Packages", "url": reverse("packages")},
            {"label": "Packages Details"},
        ]
        return ctx
