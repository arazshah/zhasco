# راهنمای استقرار روی Coolify

سایت به‌صورت یک کانتینر Docker (Django + gunicorn + WhiteNoise + SQLite) اجرا می‌شود. تنها چیزی که باید ماندگار باشد پوشه `/app/data` است (دیتابیس و فایل‌های آپلودشده).

## ۱. ساخت منبع (Resource)
1. در Coolify: **New Resource → Public/Private Repository** و ریپوی `arazshah/zhasco` را انتخاب کنید (شاخه `main`).
2. **Build Pack = Dockerfile** (پیش‌فرض). **Ports Exposes = 8000**.
3. دامنه: `https://zhasco.ir` (و در صورت نیاز `https://www.zhasco.ir`). Coolify گواهی SSL را خودکار می‌گیرد.

## ۲. Persistent Storage (بسیار مهم)
در تب **Storages** یک Volume با مسیر داخل کانتینر `/app/data` اضافه کنید. بدون این کار با هر دیپلوی، دیتابیس و تصاویر پاک می‌شود.

## ۳. متغیرهای محیطی
**فقط یک متغیر الزامی است:**

| نام | مقدار |
|---|---|
| `DJANGO_SECRET_KEY` | یک رشته تصادفی بلند، مثلاً خروجی `python3 -c "import secrets;print(secrets.token_urlsafe(60))"` |

بقیه مقدار پیش‌فرض دارند و فقط در صورت نیاز تغییرشان دهید:

| نام | پیش‌فرض |
|---|---|
| `DJANGO_ALLOWED_HOSTS` | `zhasco.ir,www.zhasco.ir,localhost,127.0.0.1` |
| `DJANGO_CSRF_TRUSTED_ORIGINS` | `https://zhasco.ir,https://www.zhasco.ir` |
| `DJANGO_SUPERUSER_USERNAME` / `DJANGO_SUPERUSER_PASSWORD` | `admin` / `ZhAS-Change-Me-1405` |
| `WEB_CONCURRENCY` | `2` |

**`DJANGO_DEBUG` را تنظیم نکنید.**

### ورود اول به داشبورد
اولین مدیر خودکار با نام کاربری `admin` و رمز اولیه `ZhAS-Change-Me-1405` ساخته می‌شود. به `/admin/` بروید؛ سایت شما را **مجبور به تغییر رمز** می‌کند و تا آن موقع به هیچ بخشی دسترسی نمی‌دهد.
چون رمز اولیه در ریپو نوشته شده، **بلافاصله بعد از دیپلوی** وارد شوید و رمز را عوض کنید. (اگر می‌خواهید رمز اولیه دیگری باشد، `DJANGO_SUPERUSER_PASSWORD` را قبل از اولین دیپلوی بگذارید.)

## ۴. دیپلوی
با زدن Deploy، در هر شروع کانتینر خودکار این کارها انجام می‌شود:
- `migrate`
- `seed_initial_data`: فقط جدول‌های **خالی** را با داده اولیه (۱۵۲ پروژه، تیم، دفاتر، گواهینامه‌ها، متن‌ها) پر می‌کند و هرگز محتوای ویرایش‌شده در داشبورد را بازنویسی نمی‌کند.
- `ensure_superuser`: اگر مدیری وجود نداشت، مدیر اولیه را (با اجبار به تغییر رمز) می‌سازد.

سپس سایت روی `https://zhasco.ir` و داشبورد روی `https://zhasco.ir/admin/` در دسترس است.

## ۵. به‌روزرسانی
هر `git push` روی `main` را می‌توانید با Webhook/Auto Deploy در Coolify به دیپلوی خودکار وصل کنید. داده‌ها روی Volume می‌مانند.

## ۶. پشتیبان‌گیری
فقط پوشه `/app/data` را (روزانه) کپی کنید: `db.sqlite3` و `media/`. در Coolify می‌توانید برای Volume، Backup زمان‌بندی‌شده تعریف کنید.

## ۷. عیب‌یابی
- خطای `DisallowedHost` یا `CSRF verification failed`: دو متغیر `DJANGO_ALLOWED_HOSTS` و `DJANGO_CSRF_TRUSTED_ORIGINS` را با دامنه واقعی بررسی کنید.
- تصاویر بعد از دیپلوی نیستند: Volume روی `/app/data` تنظیم نشده است.
- ورود به داشبورد ممکن نیست یا رمز را فراموش کرده‌اید: در Terminal کانتینر `python manage.py changepassword admin` را اجرا کنید.

## ۸. DNS دامنه
رکوردهای `A` برای `@` و `www` باید به **آی‌پی سرور Coolify** اشاره کنند (نه آی‌پی‌های پیش‌فرض/پارکینگ هاست). رکوردهای ایمیل (MX/SPF/DKIM/DMARC چابکان) را دست نزنید.

## ۹. ایمیل سازمانی (info@zhasco.ir)
در داشبورد، منوی **ارتباطات ← صندوق ایمیل**: دریافت ایمیل‌های جدید (IMAP)، خواندن، پاسخ و نوشتن ایمیل جدید (SMTP).
فقط یک متغیر لازم است:

| نام | مقدار |
|---|---|
| `MAIL_PASSWORD` | رمز صندوق `info@zhasco.ir` در چابکان |

بقیه پیش‌فرض دارند: `MAIL_USER=info@zhasco.ir`، IMAP: `t1.mail.chabokan.net:993`، SMTP: `t1.mail.chabokan.net:587` (STARTTLS).
نکته‌ها: ایمیل‌ها هنگام باز کردن صندوق (هر ۵ دقیقه) و با دکمه «دریافت ایمیل‌های جدید» همگام می‌شوند؛ تصاویر و اسکریپت داخل ایمیل‌های دریافتی حذف می‌شود؛ پیوست‌ها نمایش داده نمی‌شوند (برای آن‌ها از وب‌میل چابکان استفاده کنید) و ارسال پیوست هنوز پشتیبانی نمی‌شود.
