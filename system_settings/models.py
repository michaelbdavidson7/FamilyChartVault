from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models


def default_time_zone():
    return getattr(settings, "TIME_ZONE", "America/New_York")


class SystemSettings(models.Model):
    singleton_id = models.PositiveSmallIntegerField(
        default=1, unique=True, editable=False
    )
    time_zone = models.CharField(
        max_length=64,
        default=default_time_zone,
        help_text="Used to display exact times, such as encounters, observations, and imports.",
    )
    app_lock_enabled = models.BooleanField(
        "Require sign-in and enable lock screen",
        default=False,
        help_text="Opt in to sign-in and the manual lock screen for this local app.",
    )
    lock_shortcut_enabled = models.BooleanField(
        default=False,
        help_text="Allow Ctrl+Shift+L to lock the desktop app when the lock screen is enabled.",
    )
    login_lockout_enabled = models.BooleanField(
        default=False,
        help_text="Opt in to temporary lockouts after repeated failed sign-in attempts.",
    )
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "System Settings"
        verbose_name_plural = "System Settings"

    def __str__(self):
        return "System Settings"

    def save(self, *args, **kwargs):
        self.singleton_id = 1
        super().save(*args, **kwargs)

    def clean(self):
        super().clean()
        try:
            ZoneInfo(self.time_zone)
        except ZoneInfoNotFoundError as exc:
            raise ValidationError({"time_zone": "Choose a valid time zone."}) from exc

    @classmethod
    def get_solo(cls):
        settings, _ = cls.objects.get_or_create(singleton_id=1)
        return settings
