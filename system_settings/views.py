from django.contrib import messages
from django.contrib.auth import authenticate
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.utils import timezone

from .models import SystemSettings


UNLOCK_MAX_ATTEMPTS = 5
UNLOCK_LOCKOUT_SECONDS = 15 * 60


def _clear_app_lock_session(request):
    request.session.pop("app_locked", None)
    request.session.pop("unlock_next", None)
    request.session.pop("unlock_failures", None)
    request.session.pop("unlock_locked_until", None)


@login_required
def lock_app(request):
    if not SystemSettings.get_solo().app_lock_enabled:
        _clear_app_lock_session(request)
        messages.info(
            request, "App lock is off. Turn it on in Settings before using Lock app."
        )
        return redirect("admin:index")

    request.session["app_locked"] = True
    request.session.pop("unlock_next", None)
    return redirect("app_unlock")


@login_required
def unlock_app(request):
    if not SystemSettings.get_solo().app_lock_enabled:
        _clear_app_lock_session(request)
        return redirect("admin:index")

    locked_until = request.session.get("unlock_locked_until")

    if locked_until and timezone.now().timestamp() < locked_until:
        remaining_seconds = int(locked_until - timezone.now().timestamp())
        return render(
            request,
            "unlock.html",
            {
                "locked_out": True,
                "remaining_seconds": max(remaining_seconds, 1),
            },
        )

    if request.method == "POST":
        password = request.POST.get("password", "")
        user = authenticate(
            request,
            username=request.user.get_username(),
            password=password,
        )

        if user is not None:
            request.session.pop("app_locked", None)
            request.session.pop("unlock_failures", None)
            request.session.pop("unlock_locked_until", None)
            next_url = request.session.pop("unlock_next", None) or "/admin/"
            return redirect(next_url)

        failures = int(request.session.get("unlock_failures", 0)) + 1
        request.session["unlock_failures"] = failures

        if failures >= UNLOCK_MAX_ATTEMPTS:
            request.session["unlock_locked_until"] = (
                timezone.now().timestamp() + UNLOCK_LOCKOUT_SECONDS
            )
            messages.error(
                request, "Too many unlock attempts. Wait a few minutes and try again."
            )
        else:
            messages.error(request, "That password did not unlock HolyFHIR.")

    return render(request, "unlock.html", {"locked_out": False})
