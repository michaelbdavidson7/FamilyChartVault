from .models import SystemSettings


def system_settings(request):
    try:
        settings = SystemSettings.get_solo()
    except Exception:
        settings = None

    app_lock_enabled = bool(settings and settings.app_lock_enabled)

    return {
        "holyfhir_system_settings": settings,
        "holyfhir_app_lock_enabled": app_lock_enabled,
        "holyfhir_lock_shortcut_enabled": bool(
            app_lock_enabled and settings.lock_shortcut_enabled
        ),
    }
