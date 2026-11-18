from unittest import mock

from django.contrib.auth import get_user_model
from django.core import mail as djmail
from django.test import TestCase, override_settings
from django.urls import reverse

from core import mail as mailer
from core.models import MailMessage

RAW = (b"From: =?utf-8?b?2LnZhNuM?= <ali@example.com>\r\nTo: info@zhasco.ir\r\nSubject: =?utf-8?b?2LPZhNin2YU=?=\r\n"
       b"Date: Wed, 18 Nov 2026 10:00:00 +0330\r\nMIME-Version: 1.0\r\nContent-Type: multipart/alternative; boundary=b\r\n\r\n"
       b"--b\r\nContent-Type: text/plain; charset=utf-8\r\n\r\nhello text\r\n--b\r\nContent-Type: text/html; charset=utf-8\r\n\r\n"
       b"<p>hello</p><script>alert(1)</script><img src=http://t/x.gif>\r\n--b--\r\n")


class FakeIMAP:
    def __init__(self, *a, **k): pass
    def login(self, *a): return "OK", []
    def select(self, *a, **k): return "OK", [b"1"]
    def uid(self, cmd, *a):
        if cmd == "SEARCH": return "OK", [b"7 8"]
        return "OK", [(b"1 (UID 7 BODY[] {10}", RAW), b")"]
    def logout(self): pass


@override_settings(MAIL_PASSWORD="x", EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend")
class MailTests(TestCase):
    def test_sync_parses_and_sanitises(self):
        with mock.patch("core.mail.imaplib.IMAP4_SSL", FakeIMAP):
            n = mailer.sync_inbox()
        self.assertEqual(n, 2)
        m = MailMessage.objects.filter(direction="in").first()
        self.assertEqual(m.subject, "سلام")
        self.assertEqual(m.from_addr, "ali@example.com")
        self.assertIn("hello", m.body_text)
        self.assertNotIn("script", m.body_html)
        self.assertNotIn("<img", m.body_html)
        with mock.patch("core.mail.imaplib.IMAP4_SSL", FakeIMAP):
            mailer.sync_inbox()  # idempotent: nothing new beyond uid 8
        self.assertEqual(MailMessage.objects.filter(direction="in").count(), 2)

    def test_send_logs_copy(self):
        mailer.send("a@example.com, b@example.com", "موضوع", "متن")
        self.assertEqual(len(djmail.outbox), 1)
        self.assertEqual(djmail.outbox[0].to, ["a@example.com", "b@example.com"])
        self.assertEqual(MailMessage.objects.get(direction="out").subject, "موضوع")

    @override_settings(MAIL_PASSWORD="")
    def test_not_configured(self):
        with self.assertRaises(mailer.MailError):
            mailer.send("a@example.com", "s", "b")

    def test_admin_pages_and_compose(self):
        u = get_user_model().objects.create_superuser("root", "", "pw-12345-xx")
        self.client.force_login(u)
        with mock.patch("core.mail.imaplib.IMAP4_SSL", FakeIMAP):
            self.assertEqual(self.client.get(reverse("admin:core_mailmessage_changelist")).status_code, 200)
        m = MailMessage.objects.filter(direction="in").first()
        self.assertEqual(self.client.get(reverse("admin:core_mailmessage_change", args=[m.pk])).status_code, 200)
        m.refresh_from_db(); self.assertTrue(m.is_read)
        r = self.client.get(reverse("admin:core_mailmessage_compose") + f"?reply={m.pk}")
        self.assertEqual(r.status_code, 200, r.get("Location"))
        self.assertContains(r, "ali@example.com")
        r = self.client.post(reverse("admin:core_mailmessage_compose"), {"to": "ali@example.com", "subject": "Re", "body": "ok"})
        self.assertEqual(r.status_code, 302)
        self.assertEqual(len(djmail.outbox), 1)
        r = self.client.post(reverse("admin:core_mailmessage_compose"), {"to": "not-an-email", "subject": "Re", "body": "ok"})
        self.assertEqual(r.status_code, 200)


class MailSettingsTests(TestCase):
    def setUp(self):
        self.su = get_user_model().objects.create_superuser("root", "", "pw-12345-xx")
        self.client.force_login(self.su)
        from core.models import MailSettings
        MailSettings.load()

    def test_password_saved_encrypted_and_never_shown(self):
        url = reverse("admin:core_mailsettings_change", args=[1])
        with mock.patch("core.mail.test_connection", return_value=(True, "ok")):
            r = self.client.post(url, {"user": "info@zhasco.ir", "password": "S3cret-Pass!", "from_name": "X",
                                       "imap_host": "h", "imap_port": 993, "smtp_host": "h", "smtp_port": 587})
        self.assertEqual(r.status_code, 302, r.get("Location"))
        self.assertEqual(r["Location"], reverse("admin:core_mailsettings_changelist"), r.get("Location"))
        from core.models import MailSettings
        row = MailSettings.load()
        self.assertTrue(row.has_password)
        self.assertNotIn("S3cret-Pass!", row.password_encrypted)
        self.assertEqual(mailer.conf()["password"], "S3cret-Pass!")
        self.assertNotContains(self.client.get(url), "S3cret-Pass!")
        # blank password keeps the saved one
        with mock.patch("core.mail.test_connection", return_value=(True, "ok")):
            self.client.post(url, {"user": "info@zhasco.ir", "password": "", "from_name": "Y",
                                   "imap_host": "h", "imap_port": 993, "smtp_host": "h", "smtp_port": 587})
        self.assertEqual(mailer.conf()["password"], "S3cret-Pass!")

    def test_wrong_secret_key_means_not_configured(self):
        from core import secrets as sb
        token = sb.encrypt("abc")
        with override_settings(SECRET_KEY="another-key"):
            self.assertEqual(sb.decrypt(token), "")

    def test_staff_without_superuser_cannot_open_mail_settings(self):
        staff = get_user_model().objects.create_user("st", "", "pw-12345-xx", is_staff=True)
        self.client.force_login(staff)
        r = self.client.get(reverse("admin:core_mailsettings_change", args=[1]))
        self.assertIn(r.status_code, (302, 403))

    def test_conf_prefers_db_then_env(self):
        with override_settings(MAIL_PASSWORD="envpw"):
            self.assertEqual(mailer.conf()["password"], "envpw")
