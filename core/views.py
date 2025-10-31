from django.views.generic import TemplateView
from catalog.models import Service, ServicePackage

class HomeView(TemplateView):
    template_name = "home.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["services_count"] = Service.objects.count()
        ctx["packages_count"] = ServicePackage.objects.count()
        ctx["featured_services"] = Service.objects.order_by("name")[:6]
        ctx["featured_packages"] = ServicePackage.objects.order_by("price_cents")[:3]
        return ctx
