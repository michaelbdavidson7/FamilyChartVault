import hashlib

from django.conf import settings
from django.contrib.admin.forms import AdminAuthenticationForm
from django.core.exceptions import ValidationError
from django.db import OperationalError, ProgrammingError
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from patients.models import LoginLockout
from system_settings.models import SystemSettings


def _login_lockout_enabled():
    try:
        return SystemSettings.get_solo().login_lockout_enabled
    except (OperationalError, ProgrammingError):
        return False


def _lockout_key(value):
    digest = hashlib.sha256(str(value).encode("utf-8")).hexdigest()
    return digest


def _client_identifier(request):
    if request is None:
        return "unknown"

    return request.META.get("REMOTE_ADDR", "unknown")


def _get_lockout(scope, key):
    try:
        lockout, _ = LoginLockout.objects.get_or_create(
            scope=scope,
            key=key,
        )
    except (OperationalError, ProgrammingError):
        return None

    return lockout


def _increment_failure(scope, key, limit, timeout):
    lockout = _get_lockout(scope, key)

    if lockout is None:
        return

    lockout.failure_count += 1

    if lockout.failure_count >= limit:
        lockout.locked_until = timezone.now() + timezone.timedelta(seconds=timeout)

    lockout.save(update_fields=["failure_count", "locked_until", "updated_at"])


def _is_locked(scope, key):
    lockout = _get_lockout(scope, key)

    if lockout is None:
        return False

    if lockout.is_locked():
        return True

    if lockout.locked_until is not None:
        lockout.delete()

    return False


def _clear_failure(scope, key):
    try:
        LoginLockout.objects.filter(scope=scope, key=key).delete()
    except (OperationalError, ProgrammingError):
        pass


class RateLimitedAdminAuthenticationForm(AdminAuthenticationForm):
    """
    Adds opt-in local brute-force protection to Django Admin login.
    """

    error_messages = {
        **AdminAuthenticationForm.error_messages,
        "locked": _(
            "Too many failed login attempts. Wait a few minutes and try again."
        ),
    }

    def clean(self):
        if not _login_lockout_enabled():
            return super().clean()

        username = self.cleaned_data.get("username", "")
        client = _client_identifier(self.request)
        timeout = settings.HOLYFHIR_LOGIN_LOCKOUT_SECONDS
        username_limit = settings.HOLYFHIR_LOGIN_MAX_ATTEMPTS_PER_USERNAME
        client_limit = settings.HOLYFHIR_LOGIN_MAX_ATTEMPTS_PER_CLIENT

        username_key = _lockout_key(username.lower())
        client_key = _lockout_key(client)

        if _is_locked(LoginLockout.SCOPE_USERNAME, username_key):
            raise ValidationError(
                self.error_messages["locked"],
                code="locked",
            )

        if _is_locked(LoginLockout.SCOPE_CLIENT, client_key):
            raise ValidationError(
                self.error_messages["locked"],
                code="locked",
            )

        try:
            cleaned_data = super().clean()
        except ValidationError:
            _increment_failure(
                LoginLockout.SCOPE_USERNAME, username_key, username_limit, timeout
            )
            _increment_failure(
                LoginLockout.SCOPE_CLIENT, client_key, client_limit, timeout
            )
            raise

        _clear_failure(LoginLockout.SCOPE_USERNAME, username_key)
        _clear_failure(LoginLockout.SCOPE_CLIENT, client_key)
        return cleaned_data
