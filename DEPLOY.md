# راهنمای استقرار روی Coolify

سایت به‌صورت یک کانتینر Docker (Django + gunicorn + WhiteNoise + SQLite) اجرا می‌شود. تنها چیزی که باید ماندگار باشد پوشه `/app/data` است (دیتابیس و فایل‌های آپلودشده).

## ۱. ساخت منبع (Resource)
1. در Coolify: **New Resource → Public/Private Repository** و ریپوی `arazshah/zhasco` را انتخاب کنید (شاخه `main`).
2. **Build Pack = Dockerfile** (پیش‌فرض). **Ports Exposes = 8000**.
3. دامنه: `https://zhasco.ir` (و در صورت نیاز `https://www.zhasco.ir`). Coolify گواهی SSL را خودکار می‌گیرد.

## ۲. Persistent Storage (بسیار مهم)
در تب **Storages** یک Volume با مسیر داخل کانتینر `/app/data` اضافه کنید. بدون این کار با هر دیپلوی، دیتابیس و تصاویر پاک می‌شود.

## ۳. متغیرهای محیطی (Environment Variables)
| نام | مقدار |
|---|---|
| `DJANGO_SECRET_KEY` | یک رشته تصادفی بلند (مثلاً `python -c "import secrets;print(secrets.token_urlsafe(60))"`) |
| `DJANGO_ALLOWED_HOSTS` | `zhasco.ir,www.zhasco.ir` |
| `DJANGO_CSRF_TRUSTED_ORIGINS` | `https://zhasco.ir,https://www.zhasco.ir` |
| `DJANGO_SUPERUSER_USERNAME` | نام کاربری مدیر |
| `DJANGO_SUPERUSER_PASSWORD` | گذرواژه قوی (فقط برای ساخت اولین مدیر؛ پس از اولین اجرا می‌توانید حذفش کنید) |
| `DJANGO_SUPERUSER_EMAIL` | اختیاری |
| `WEB_CONCURRENCY` | اختیاری، تعداد workerها (پیش‌فرض ۲) |

نمونه در `.env.example` هست. **`DJANGO_DEBUG` را تنظیم نکنید** (پیش‌فرض خاموش است).

## ۴. دیپلوی
با زدن Deploy، در هر شروع کانتینر خودکار این کارها انجام می‌شود:
- `migrate`
- `seed_initial_data`: فقط جدول‌های **خالی** را با داده اولیه (۱۵۲ پروژه، تیم، دفاتر، گواهینامه‌ها، متن‌ها) پر می‌کند و هرگز محتوای ویرایش‌شده در داشبورد را بازنویسی نمی‌کند.
- `ensure_superuser`: اگر مدیری وجود نداشت، از روی متغیرهای بالا می‌سازد.

سپس سایت روی `https://zhasco.ir` و داشبورد روی `https://zhasco.ir/admin/` در دسترس است.

## ۵. به‌روزرسانی
هر `git push` روی `main` را می‌توانید با Webhook/Auto Deploy در Coolify به دیپلوی خودکار وصل کنید. داده‌ها روی Volume می‌مانند.

## ۶. پشتیبان‌گیری
فقط پوشه `/app/data` را (روزانه) کپی کنید: `db.sqlite3` و `media/`. در Coolify می‌توانید برای Volume، Backup زمان‌بندی‌شده تعریف کنید.

## ۷. عیب‌یابی
- خطای `DisallowedHost` یا `CSRF verification failed`: دو متغیر `DJANGO_ALLOWED_HOSTS` و `DJANGO_CSRF_TRUSTED_ORIGINS` را با دامنه واقعی بررسی کنید.
- تصاویر بعد از دیپلوی نیستند: Volume روی `/app/data` تنظیم نشده است.
- ورود به داشبورد ممکن نیست: متغیرهای `DJANGO_SUPERUSER_*` را بگذارید و Redeploy کنید، یا در Terminal کانتینر: `python manage.py createsuperuser`.
