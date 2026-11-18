"""Django settings for the Zharf Azaran Sadr company website.

All deploy-specific values come from environment variables (see DEPLOY.md).
"""
import os
from pathlib import Path

from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _

BASE_DIR = Path(__file__).resolve().parent.parent


def env_bool(name, default=False):
    return os.environ.get(name, str(default)).strip().lower() in ("1", "true", "yes", "on")


def env_list(name, default=""):
    return [x.strip() for x in os.environ.get(name, default).split(",") if x.strip()]


DEBUG = env_bool("DJANGO_DEBUG", False)

SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY", "")
if not SECRET_KEY:
    if DEBUG:
        SECRET_KEY = "dev-insecure-key-change-me"
    else:
        raise RuntimeError("DJANGO_SECRET_KEY is not set. Add it in the environment (see DEPLOY.md).")

ALLOWED_HOSTS = env_list("DJANGO_ALLOWED_HOSTS", "zhasco.ir,www.zhasco.ir,localhost,127.0.0.1")
CSRF_TRUSTED_ORIGINS = env_list("DJANGO_CSRF_TRUSTED_ORIGINS", "https://zhasco.ir,https://www.zhasco.ir")

# Persistent data (SQLite db + uploaded media) lives in one directory => one Coolify volume.
DATA_DIR = Path(os.environ.get("DATA_DIR", BASE_DIR / "data"))
DATA_DIR.mkdir(parents=True, exist_ok=True)

INSTALLED_APPS = [
    "unfold",
    "unfold.contrib.filters",
    "unfold.contrib.forms",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.sitemaps",
    "core",
    "projects",
    "news",
    "careers",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "core.middleware.ForcePasswordChangeMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"
WSGI_APPLICATION = "config.wsgi.application"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "core.context_processors.site",
            ],
        },
    },
]

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": DATA_DIR / "db.sqlite3",
        "OPTIONS": {
            "transaction_mode": "IMMEDIATE",
            "timeout": 20,
            "init_command": "PRAGMA journal_mode=WAL; PRAGMA synchronous=NORMAL; PRAGMA foreign_keys=ON;",
        },
    }
}
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator", "OPTIONS": {"min_length": 8}},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LANGUAGE_CODE = "fa"
LANGUAGES = [("fa", "فارسی")]
TIME_ZONE = "Asia/Tehran"
USE_I18N = True
USE_TZ = True

STATIC_URL = "/static/"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles"
STORAGES = {
    "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage"
        if not DEBUG
        else "django.contrib.staticfiles.storage.StaticFilesStorage"
    },
}
WHITENOISE_MAX_AGE = 31536000 if not DEBUG else 0

MEDIA_URL = "/media/"
MEDIA_ROOT = DATA_DIR / "media"
FILE_UPLOAD_MAX_MEMORY_SIZE = 5 * 1024 * 1024
DATA_UPLOAD_MAX_MEMORY_SIZE = 8 * 1024 * 1024

# --- security -------------------------------------------------------------
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
USE_X_FORWARDED_HOST = True
SECURE_SSL_REDIRECT = env_bool("DJANGO_SSL_REDIRECT", False)
SESSION_COOKIE_SECURE = not DEBUG
CSRF_COOKIE_SECURE = not DEBUG
SESSION_COOKIE_HTTPONLY = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_REFERRER_POLICY = "strict-origin-when-cross-origin"
X_FRAME_OPTIONS = "SAMEORIGIN"
if not DEBUG and env_bool("DJANGO_HSTS", True):
    SECURE_HSTS_SECONDS = 31536000
    SECURE_HSTS_INCLUDE_SUBDOMAINS = False

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {"console": {"class": "logging.StreamHandler"}},
    "root": {"handlers": ["console"], "level": os.environ.get("DJANGO_LOG_LEVEL", "INFO")},
}

# --- admin dashboard (Unfold) --------------------------------------------
UNFOLD = {
    "SITE_TITLE": "مدیریت ژرف آذران صدر",
    "SITE_HEADER": "ژرف آذران صدر",
    "SITE_SUBHEADER": "داشبورد مدیریت وب‌سایت",
    "SITE_URL": "/",
    "SITE_ICON": lambda request: "/static/img/logo-bird.png",
    "SITE_FAVICONS": [
        {"rel": "icon", "sizes": "32x32", "type": "image/png", "href": lambda request: "/static/img/favicon.png"},
    ],
    "SHOW_HISTORY": True,
    "SHOW_VIEW_ON_SITE": True,
    "BORDER_RADIUS": "10px",
    "COLORS": {
        "primary": {
            "50": "250 240 251", "100": "243 224 245", "200": "230 193 235", "300": "212 150 220",
            "400": "187 98 199", "500": "158 56 168", "600": "139 40 144", "700": "115 33 120",
            "800": "95 30 99", "900": "78 28 82", "950": "50 12 54",
        },
    },
    "STYLES": [lambda request: "/static/css/admin.css"],
    "DASHBOARD_CALLBACK": "core.dashboard.dashboard_callback",
    "SIDEBAR": {
        "show_search": True,
        "show_all_applications": False,
        "navigation": [
            {
                "title": "محتوای سایت",
                "separator": True,
                "items": [
                    {"title": "پروژه‌ها", "icon": "engineering", "link": reverse_lazy("admin:projects_project_changelist")},
                    {"title": "حوزه‌های خدمات", "icon": "construction", "link": reverse_lazy("admin:projects_servicearea_changelist")},
                    {"title": "اخبار و مقالات", "icon": "newspaper", "link": reverse_lazy("admin:news_post_changelist")},
                    {"title": "کارفرمایان", "icon": "business", "link": reverse_lazy("admin:core_client_changelist")},
                ],
            },
            {
                "title": "شرکت",
                "separator": True,
                "items": [
                    {"title": "اعضای تیم", "icon": "groups", "link": reverse_lazy("admin:core_teammember_changelist")},
                    {"title": "ساختار سازمانی", "icon": "account_tree", "link": reverse_lazy("admin:core_orgunit_changelist")},
                    {"title": "گواهینامه‌ها", "icon": "verified", "link": reverse_lazy("admin:core_certificate_changelist")},
                    {"title": "دفاتر و شعب", "icon": "location_city", "link": reverse_lazy("admin:core_office_changelist")},
                    {"title": "سیاست‌ها و اهداف", "icon": "flag", "link": reverse_lazy("admin:core_valueitem_changelist")},
                    {"title": "تاریخچه", "icon": "timeline", "link": reverse_lazy("admin:core_timelineevent_changelist")},
                    {"title": "منابع پژوهش و توسعه", "icon": "science", "link": reverse_lazy("admin:core_rndresource_changelist")},
                ],
            },
            {
                "title": "ارتباطات",
                "separator": True,
                "items": [
                    {"title": "صندوق ایمیل", "icon": "inbox", "link": reverse_lazy("admin:core_mailmessage_changelist"),
                     "badge": "core.dashboard.unread_mail_badge"},
                    {"title": "پیام‌های فرم تماس", "icon": "mail", "link": reverse_lazy("admin:core_contactmessage_changelist"),
                     "badge": "core.dashboard.unread_messages_badge"},
                    {"title": "آگهی‌های شغلی", "icon": "work", "link": reverse_lazy("admin:careers_jobposting_changelist")},
                    {"title": "رزومه‌های دریافتی", "icon": "description", "link": reverse_lazy("admin:careers_jobapplication_changelist"),
                     "badge": "core.dashboard.unread_applications_badge"},
                ],
            },
            {
                "title": "تنظیمات",
                "separator": True,
                "items": [
                    {"title": "تنظیمات سایت", "icon": "settings", "link": reverse_lazy("admin:core_sitesettings_changelist")},
                    {"title": "تنظیمات ایمیل", "icon": "key", "link": reverse_lazy("admin:core_mailsettings_changelist"),
                     "permission": lambda request: request.user.is_superuser},
                    {"title": "استان‌ها و نقشه", "icon": "map", "link": reverse_lazy("admin:core_province_changelist")},
                    {"title": "کاربران", "icon": "person", "link": reverse_lazy("admin:auth_user_changelist")},
                    {"title": "گروه‌ها", "icon": "lock", "link": reverse_lazy("admin:auth_group_changelist")},
                ],
            },
        ],
    },
}
LOGIN_URL = "admin:login"
LOGIN_REDIRECT_URL = "/admin/"

# --- company mailbox (info@zhasco.ir on Chabokan) --------------------------
# Defaults only: the password and servers are normally entered in the dashboard (تنظیمات ایمیل);
# MAIL_PASSWORD is an optional fallback.
MAIL_USER = os.environ.get("MAIL_USER", "info@zhasco.ir")
MAIL_PASSWORD = os.environ.get("MAIL_PASSWORD", "")
MAIL_IMAP_HOST = os.environ.get("MAIL_IMAP_HOST", "t1.mail.chabokan.net")
MAIL_IMAP_PORT = int(os.environ.get("MAIL_IMAP_PORT", "993"))
MAIL_FROM_NAME = os.environ.get("MAIL_FROM_NAME", "ژرف آذران صدر")
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = os.environ.get("MAIL_SMTP_HOST", "t1.mail.chabokan.net")
EMAIL_PORT = int(os.environ.get("MAIL_SMTP_PORT", "587"))
EMAIL_USE_TLS = True
EMAIL_HOST_USER = MAIL_USER
EMAIL_HOST_PASSWORD = MAIL_PASSWORD
EMAIL_TIMEOUT = 20
DEFAULT_FROM_EMAIL = f"{MAIL_FROM_NAME} <{MAIL_USER}>"
