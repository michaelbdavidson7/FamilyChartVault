from django import forms
from django.conf import settings
from django.contrib import admin
from django.contrib import messages
from django.utils import timezone

from .env_sync import update_env_value
from .models import SystemSettings
from .time_zones import time_zone_choices


class SystemSettingsAdminForm(forms.ModelForm):
    time_zone = forms.ChoiceField(
        choices=time_zone_choices,
        help_text=(
            "Used for displaying exact times. Calendar-only medical dates, such as birth dates, "
            "stay stored as dates and are not shifted by time zone."
        ),
    )

    class Meta:
        model = SystemSettings
        fields = "__all__"


@admin.register(SystemSettings)
class SystemSettingsAdmin(admin.ModelAdmin):
    form = SystemSettingsAdminForm
    fieldsets = (
        (
            "Local time",
            {
                "fields": ("time_zone",),
                "description": (
                    "HolyFHIR stores medical calendar dates as dates. This setting controls how exact timestamps "
                    "are displayed, such as observations, encounters, imports, and security events."
                ),
            },
        ),
        (
            "Locking",
            {
                "fields": (
                    "app_lock_enabled",
                    "lock_shortcut_enabled",
                    "login_lockout_enabled",
                ),
                "description": (
                    "Sign-in and locking features are off by default. Turn them on only if this computer needs extra local protection."
                ),
            },
        ),
        (
            "Meta",
            {
                "fields": ("updated_at",),
            },
        ),
    )
    readonly_fields = ("updated_at",)

    def has_add_permission(self, request):
        return not SystemSettings.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)

        if "time_zone" in form.changed_data:
            settings.TIME_ZONE = obj.time_zone
            timezone.get_default_timezone.cache_clear()
            timezone.activate(obj.time_zone)

            if update_env_value("TIME_ZONE", obj.time_zone):
                messages.success(request, "Time zone saved for future app starts.")
            else:
                messages.warning(
                    request,
                    "Time zone saved in app settings, but .env was not found to update future app starts.",
                )
