from django.shortcuts import redirect
from django.conf import settings
from django.urls import reverse


class LoginRequiredMiddleware:
    EXEMPT_URLS = None

    def __init__(self, get_response):
        self.get_response = get_response
        # Build exempt list once at startup
        login = settings.LOGIN_URL
        logout = reverse("core:logout")
        register = reverse("core:register")

        self.EXEMPT_URLS = [
            login,
            logout,
            register,
            "/admin/login/",       # allow admin login
        ]

    def __call__(self, request):
        path = request.path

        if request.user.is_authenticated:
            return self.get_response(request)

        # Allow anon users on login/logout/register
        if any(path.startswith(u) for u in self.EXEMPT_URLS):
            return self.get_response(request)

        # Reject all other URLs
        return redirect(settings.LOGIN_URL)
