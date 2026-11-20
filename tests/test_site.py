import re

from django.core import signing
from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.management import call_command
from django.test import TestCase, override_settings
from django.urls import reverse

from careers.models import JobApplication
from core.models import ContactMessage, Province
from core.templatetags.zh import clean_html, fa, fa_num, level
from projects.models import Project


LOCMEM = {"default": {"BACKEND": "django.core.cache.backends.locmem.LocMemCache"}}


def challenge(client, url):
    """Fetch a form page and return the solved anti-spam fields."""
    html = client.get(url).content.decode()
    token = re.search(r'name="ts_token" value="([^"]+)"', html).group(1)
    d = signing.loads(token, salt="zhasco.antispam.v1")
    return {"ts_token": token, "captcha": str(d["a"] + d["b"])}


@override_settings(CACHES=LOCMEM, ANTISPAM_MIN_SECONDS=0)
class SiteTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        call_command("seed_initial_data", verbosity=0)

    def setUp(self):
        cache.clear()

    def test_seed_counts(self):
        self.assertEqual(Province.objects.count(), 31)
        self.assertEqual(Project.objects.count(), 152)
        self.assertEqual(Project.objects.values("province").distinct().count(), 9)

    def test_public_pages_ok(self):
        pid = Project.objects.first().pk
        for url in ["/", "/about/", "/team/", "/quality/", "/rnd/", "/contact/", "/projects/", f"/projects/{pid}/",
                    "/projects/?province=south-khorasan&status=ongoing&q=آبیاری", "/services/", "/services/irrigation/",
                    "/news/", "/careers/", "/careers/apply/", "/robots.txt", "/sitemap.xml"]:
            with self.subTest(url=url):
                self.assertEqual(self.client.get(url).status_code, 200)

    def test_404(self):
        self.assertEqual(self.client.get("/nope/").status_code, 404)

    def test_home_map_marks_only_provinces_with_projects(self):
        html = self.client.get("/").content.decode()
        self.assertEqual(html.count('class="prov is-active'), 9)

    def test_province_api(self):
        r = self.client.get("/api/provinces/south-khorasan/")
        data = r.json()
        self.assertEqual(data["count"], 63)
        self.assertEqual(self.client.get("/api/provinces/nowhere/").status_code, 404)

    def test_unpublished_project_hidden_and_province_uncolored(self):
        Project.objects.filter(province__slug="kordestan").update(is_published=False)
        self.assertEqual(self.client.get("/api/provinces/kordestan/").json()["count"], 0)
        self.assertEqual(self.client.get("/").content.decode().count('class="prov is-active'), 8)
        p = Project.objects.filter(is_published=False).first()
        self.assertEqual(self.client.get(f"/projects/{p.pk}/").status_code, 404)

    def test_contract_number_hidden_by_default(self):
        p = Project.objects.exclude(contract_number="").first()
        self.assertNotIn(p.contract_number, self.client.get(f"/projects/{p.pk}/").content.decode().replace("۰", "0"))

    def test_contact_form(self):
        r = self.client.post("/contact/", {"name": "علی", "phone": "0912", "message": "سلام", **challenge(self.client, "/contact/")})
        self.assertEqual(r.status_code, 302)
        self.assertEqual(ContactMessage.objects.count(), 1)

    def test_contact_requires_phone_or_email(self):
        self.client.post("/contact/", {"name": "علی", "message": "سلام", **challenge(self.client, "/contact/")})
        self.assertEqual(ContactMessage.objects.count(), 0)

    def test_contact_honeypot(self):
        self.client.post("/contact/", {"name": "bot", "phone": "1", "message": "x", "website": "http://spam"})
        self.assertEqual(ContactMessage.objects.count(), 0)

    def test_resume_upload_validation(self):
        bad = SimpleUploadedFile("x.exe", b"MZ", content_type="application/octet-stream")
        self.client.post("/careers/apply/", {"name": "a", "phone": "1", "resume": bad, **challenge(self.client, "/careers/apply/")})
        self.assertEqual(JobApplication.objects.count(), 0)
        ok = SimpleUploadedFile("cv.pdf", b"%PDF-1.4 test", content_type="application/pdf")
        self.client.post("/careers/apply/", {"name": "a", "phone": "1", "resume": ok, **challenge(self.client, "/careers/apply/")})
        self.assertEqual(JobApplication.objects.count(), 1)

    def test_admin_requires_login(self):
        r = self.client.get("/admin/")
        self.assertEqual(r.status_code, 302)
        self.assertIn("/admin/login/", r["Location"])

    def test_admin_dashboard_and_lists(self):
        from django.contrib.auth import get_user_model
        u = get_user_model().objects.create_superuser("root", "", "pw-12345-xx")
        self.client.force_login(u)
        for name in ["admin:index", "admin:projects_project_changelist", "admin:core_sitesettings_changelist",
                     "admin:core_province_changelist", "admin:news_post_add", "admin:projects_project_add",
                     "admin:core_contactmessage_changelist", "admin:careers_jobapplication_changelist"]:
            with self.subTest(name=name):
                self.assertIn(self.client.get(reverse(name), follow=True).status_code, (200,))

    def test_filters(self):
        self.assertEqual(fa("1405/02"), "۱۴۰۵/۰۲")
        self.assertEqual(fa_num(40000), "۴۰٬۰۰۰")
        self.assertEqual([level(n) for n in (0, 1, 5, 15, 40)], [0, 1, 2, 3, 4])

    def test_clean_html_strips_scripts(self):
        out = str(clean_html('<p>سلام</p><script>alert(1)</script><a href="javascript:x()">t</a>'))
        self.assertNotIn("script", out)
        self.assertNotIn("javascript", out)
        self.assertIn("<p>سلام</p>", out)

    def test_seed_is_idempotent(self):
        call_command("seed_initial_data", verbosity=0)
        self.assertEqual(Project.objects.count(), 152)


class FirstLoginTests(TestCase):
    def test_bootstrap_admin_must_change_password(self):
        call_command("ensure_superuser", verbosity=0)
        self.assertTrue(self.client.login(username="admin", password="ZhAS-Change-Me-1405"))
        r = self.client.get("/admin/")
        self.assertEqual(r.status_code, 302)
        self.assertEqual(r["Location"], reverse("admin:password_change"))
        self.assertEqual(self.client.get(reverse("admin:password_change")).status_code, 200)
        r = self.client.post(reverse("admin:password_change"), {
            "old_password": "ZhAS-Change-Me-1405", "new_password1": "Mine-Strong-Pass-77", "new_password2": "Mine-Strong-Pass-77"})
        self.assertEqual(r.status_code, 302)
        self.assertEqual(self.client.get("/admin/").status_code, 200)

    def test_existing_superuser_is_not_touched(self):
        from django.contrib.auth import get_user_model
        get_user_model().objects.create_superuser("owner", "", "OwnerPass-12345")
        call_command("ensure_superuser", verbosity=0)
        self.assertFalse(get_user_model().objects.filter(username="admin").exists())


@override_settings(CACHES=LOCMEM, ANTISPAM_MIN_SECONDS=0)
class AntiSpamTests(TestCase):
    def setUp(self):
        cache.clear()

    def test_missing_or_wrong_answer_rejected(self):
        self.client.post("/contact/", {"name": "x", "phone": "1", "message": "m"})
        d = challenge(self.client, "/contact/"); d["captcha"] = "999"
        self.client.post("/contact/", {"name": "x", "phone": "1", "message": "m", **d})
        self.assertEqual(ContactMessage.objects.count(), 0)

    def test_persian_digits_accepted(self):
        d = challenge(self.client, "/contact/")
        d["captcha"] = d["captcha"].translate(str.maketrans("0123456789", "۰۱۲۳۴۵۶۷۸۹"))
        self.client.post("/contact/", {"name": "x", "phone": "1", "message": "m", **d})
        self.assertEqual(ContactMessage.objects.count(), 1)

    def test_token_is_one_time(self):
        d = challenge(self.client, "/contact/")
        self.client.post("/contact/", {"name": "a", "phone": "1", "message": "m", **d})
        c2 = self.client_class()  # a bot without cookies replaying the same token
        c2.post("/contact/", {"name": "b", "phone": "1", "message": "m", **d})
        self.assertEqual(ContactMessage.objects.count(), 1)

    @override_settings(ANTISPAM_MIN_SECONDS=30)
    def test_too_fast_rejected(self):
        d = challenge(self.client, "/contact/")
        self.client.post("/contact/", {"name": "a", "phone": "1", "message": "m", **d})
        self.assertEqual(ContactMessage.objects.count(), 0)

    def test_links_rejected_one_link_ok(self):
        d = challenge(self.client, "/contact/")
        self.client.post("/contact/", {"name": "a", "phone": "1", "message": "buy http://a.com http://b.com www.c.com", **d})
        self.assertEqual(ContactMessage.objects.count(), 0)
        d = challenge(self.client, "/contact/")
        self.client.post("/contact/", {"name": "a", "phone": "1", "message": "سایت ما http://a.com", **d})
        self.assertEqual(ContactMessage.objects.count(), 1)

    def test_rate_limit_per_ip_even_without_cookies(self):
        for i in range(8):
            c = self.client_class()  # new session each time, same IP
            d = challenge(c, "/contact/")
            c.post("/contact/", {"name": f"n{i}", "phone": "1", "message": f"m{i}", **d}, HTTP_X_FORWARDED_FOR="9.9.9.9")
        self.assertEqual(ContactMessage.objects.count(), 5)
        self.assertEqual(set(ContactMessage.objects.values_list("ip", flat=True)), {"9.9.9.9"})

    def test_honeypot_silently_dropped(self):
        d = challenge(self.client, "/contact/")
        self.client.post("/contact/", {"name": "bot", "phone": "1", "message": "m", "website": "http://x", **d})
        self.assertEqual(ContactMessage.objects.count(), 0)
