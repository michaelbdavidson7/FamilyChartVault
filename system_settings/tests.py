from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import TestCase, override_settings
from django.urls import reverse
from django.utils import timezone

from .env_sync import update_env_value
from .models import SystemSettings


class AppLockTests(TestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(
            username="owner",
            password="correct-password",
            is_staff=True,
            is_superuser=True,
        )

    def test_admin_auto_signs_in_local_owner_when_locking_is_disabled(self):
        response = self.client.get(reverse("admin:index"))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(int(self.client.session["_auth_user_id"]), self.user.pk)

    def test_admin_requires_sign_in_when_locking_is_enabled(self):
        SystemSettings.get_solo()
        SystemSettings.objects.update(app_lock_enabled=True)

        response = self.client.get(reverse("admin:index"))

        self.assertRedirects(
            response,
            f"{reverse('admin:login')}?next={reverse('admin:index')}",
            fetch_redirect_response=False,
        )

    def test_lock_app_is_disabled_by_default(self):
        self.client.force_login(self.user)

        response = self.client.get(reverse("app_lock"))

        self.assertRedirects(response, reverse("admin:index"))
        self.assertNotIn("app_locked", self.client.session)

    def test_existing_lock_state_is_ignored_when_disabled(self):
        self.client.force_login(self.user)
        session = self.client.session
        session["app_locked"] = True
        session.save()

        response = self.client.get(reverse("admin:index"))

        self.assertEqual(response.status_code, 200)
        self.assertNotIn("app_locked", self.client.session)

    def test_lock_redirects_to_unlock_and_blocks_admin_when_enabled(self):
        SystemSettings.get_solo()
        SystemSettings.objects.update(app_lock_enabled=True)
        self.client.force_login(self.user)

        response = self.client.get(reverse("app_lock"))

        self.assertRedirects(response, reverse("app_unlock"))
        self.assertTrue(self.client.session["app_locked"])

        response = self.client.get(reverse("admin:index"))

        self.assertRedirects(response, reverse("app_unlock"))

    def test_unlock_with_password_clears_lock_when_enabled(self):
        SystemSettings.get_solo()
        SystemSettings.objects.update(app_lock_enabled=True)
        self.client.force_login(self.user)
        session = self.client.session
        session["app_locked"] = True
        session.save()

        response = self.client.post(
            reverse("app_unlock"),
            {"password": "correct-password"},
        )

        self.assertRedirects(response, "/admin/", fetch_redirect_response=False)
        self.assertNotIn("app_locked", self.client.session)


class SystemSettingsTests(TestCase):
    def test_get_solo_uses_configured_time_zone_default(self):
        with override_settings(TIME_ZONE="America/Chicago"):
            settings = SystemSettings.get_solo()

        self.assertEqual(settings.time_zone, "America/Chicago")

    def test_locking_features_are_disabled_by_default(self):
        settings = SystemSettings.get_solo()

        self.assertFalse(settings.app_lock_enabled)
        self.assertFalse(settings.lock_shortcut_enabled)
        self.assertFalse(settings.login_lockout_enabled)

    def test_invalid_time_zone_is_rejected(self):
        settings = SystemSettings(time_zone="Not/A_Timezone")

        with self.assertRaisesMessage(ValidationError, "Choose a valid time zone."):
            settings.full_clean()

    def test_authenticated_requests_activate_system_time_zone(self):
        User = get_user_model()
        user = User.objects.create_user(
            username="owner",
            password="correct-password",
            is_staff=True,
            is_superuser=True,
        )
        SystemSettings.get_solo()
        SystemSettings.objects.update(time_zone="America/Los_Angeles")
        self.client.force_login(user)

        self.client.get(reverse("admin:index"))

        self.assertEqual(timezone.get_current_timezone_name(), "America/Los_Angeles")

    def test_env_sync_backs_up_existing_env_before_writing(self):
        with TemporaryDirectory() as temp_dir:
            env_path = Path(temp_dir) / ".env"
            env_path.write_text(
                "TIME_ZONE=America/New_York\nSECRET_KEY=keep-me\n", encoding="utf-8"
            )

            with patch.dict(
                "os.environ", {"DJANGO_ENV_FILE": str(env_path)}, clear=True
            ):
                self.assertTrue(update_env_value("TIME_ZONE", "America/Chicago"))

            backups = list(Path(temp_dir).glob(".env.backup.*"))
            backup_count = len(backups)
            backup_content = backups[0].read_text(encoding="utf-8") if backups else ""

        self.assertEqual(backup_count, 1)
        self.assertEqual(
            backup_content, "TIME_ZONE=America/New_York\nSECRET_KEY=keep-me\n"
        )
