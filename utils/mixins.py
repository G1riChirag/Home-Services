class BreadcrumbsMixin:
    def get_breadcrumbs(self):
        return []

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["breadcrumbs"] = self.get_breadcrumbs()
        return ctx
