# users/views.py
from django.contrib.auth.views import LoginView
from django.urls import reverse_lazy
from django.views.generic import CreateView, View, FormView     # <-- add FormView
from django.contrib.auth import logout
from django.shortcuts import redirect, render
from django.contrib import messages                               # <-- feedback
from django.utils.decorators import method_decorator
from django.views.decorators.http import require_GET
from django.contrib.auth.mixins import LoginRequiredMixin         # <-- ensure auth

from .forms import TwoFactorAuthenticationForm, RegistrationForm, DeleteAccountForm  # <-- add DeleteAccountForm


class LoginWith2FAView(LoginView):
    template_name = "users/login.html"
    authentication_form = TwoFactorAuthenticationForm
    def form_invalid(self, form):
        ctx = self.get_context_data(form=form)
        ctx["show_otp_modal"] = bool(getattr(form, "_show_otp_modal", False))
        ctx["otp_first_prompt"] = bool(getattr(form, "_otp_first_prompt", False))
        return self.render_to_response(ctx)


class RegisterView(CreateView):
    form_class = RegistrationForm
    template_name = "users/register.html"
    success_url = reverse_lazy("login")


class LogoutView(View):
    def post(self, request):
        logout(request)
        return redirect("home")
    def get(self, request):
        logout(request)
        return redirect("home")


# --- Delete Account ---
class DeleteAccountView(LoginRequiredMixin, FormView):
    template_name = "users/delete_account.html"
    form_class = DeleteAccountForm
    success_url = reverse_lazy("home")

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["request"] = self.request   # pass request so form knows the user & 2FA state
        return kwargs

    def form_valid(self, form):
        user = self.request.user

        # Best-effort: delete vaccination file explicitly (also handled by signal if cascade)
        prof = getattr(user, "userprofile", None) or getattr(user, "profile", None)
        if prof and getattr(prof, "vaccination_proof", None):
            try:
                prof.vaccination_proof.delete(save=False)
            except Exception:
                pass  # ignore storage errors

        # This will cascade-delete related objects due to on_delete=CASCADE in models
        user.delete()
        logout(self.request)
        messages.success(self.request, "Your account has been deleted.")
        return super().form_valid(form)
