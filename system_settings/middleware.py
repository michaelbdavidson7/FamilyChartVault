from django.contrib.auth import get_user_model, login
from django.db import OperationalError, ProgrammingError
from django.shortcuts import redirect
from django.urls import reverse
from django.utils import timezone

from .models import SystemSettings


class AppLockMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        app_settings = self._get_settings()

        if app_settings and not app_settings.app_lock_enabled:
            self._sign_in_local_owner(request)

        if request.user.is_authenticated and app_settings:
            timezone.activate(app_settings.time_zone)

        if self._should_redirect_to_unlock(request, app_settings):
            request.session["unlock_next"] = request.get_full_path()
            return redirect("app_unlock")

        return self.get_response(request)

    def _get_settings(self):
        try:
            return SystemSettings.get_solo()
        except (OperationalError, ProgrammingError):
            return None

    def _sign_in_local_owner(self, request):
        if request.user.is_authenticated:
            return

        try:
            owner = (
                get_user_model()
                .objects.filter(is_active=True, is_staff=True)
                .order_by("-is_superuser", "pk")
                .first()
            )
        except (OperationalError, ProgrammingError):
            return

        if owner is None:
            return

        login(request, owner, backend="django.contrib.auth.backends.ModelBackend")
        request.user = owner

    def _should_redirect_to_unlock(self, request, app_settings):
        if not request.user.is_authenticated:
            return False

        if not app_settings or not app_settings.app_lock_enabled:
            request.session.pop("app_locked", None)
            request.session.pop("unlock_next", None)
            return False

        if not request.session.get("app_locked"):
            return False

        allowed_paths = {
            reverse("app_unlock"),
            reverse("admin:logout"),
        }

        return request.path not in allowed_paths and not request.path.startswith(
            "/static/"
        )
