from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.views import LoginView, LogoutView
from django.urls import reverse_lazy
from django.views.generic.edit import FormView
from django.views.generic import FormView, UpdateView
from django.views import View
from django.shortcuts import redirect
from .models import SystemSettings
from .forms import SystemSettingsForm
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.http import JsonResponse


from core.forms import RegisterForm


class CustomLoginView(LoginView):
    template_name = 'login.html'


class CustomLogoutView(LogoutView):
    next_page = 'login'


class RegisterView(FormView):
    template_name = 'register.html'
    form_class = RegisterForm
    success_url = reverse_lazy('dashboard')

    def form_valid(self, form):
        user = form.save()         # save the new user
        login(self.request, user)  # log them in immediately
        return super().form_valid(form)

class SettingsView(UpdateView):
    model = SystemSettings
    form_class = SystemSettingsForm
    template_name = "settings.html"
    success_url = reverse_lazy("controller:dashboard")

    def get_object(self, queryset=None):
        # Always use the singleton instance
        settings, _ = SystemSettings.objects.get_or_create(pk=1)
        return settings
    
@method_decorator(csrf_exempt, name='dispatch')
class UpdateSettingsView(View):

    def post(self, request, *args, **kwargs):
        settings, _ = SystemSettings.objects.get_or_create(pk=1)

        mode = request.POST.get("mode")
        eco_temp = request.POST.get("eco_temperature")

        changed = False

        if mode and mode in ["auto", "manual"] and settings.mode != mode:
            settings.mode = mode
            changed = True

        if eco_temp:
            try:
                eco_temp = float(eco_temp)
                if settings.eco_temperature != eco_temp:
                    settings.eco_temperature = eco_temp
                    changed = True
            except ValueError:
                pass

        if changed:
            settings.save()

        return JsonResponse({"status": "ok", "mode": settings.mode, "eco_temperature": settings.eco_temperature})
