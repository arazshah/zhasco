# وب‌سایت مهندسین مشاور ژرف آذران صدر

Django 5 + SQLite، داشبورد مدیریت فارسی (Unfold)، صفحه اصلی با **نقشه تعاملی ایران**: استان‌هایی که پروژه منتشرشده دارند خودکار رنگی می‌شوند و با کلیک، فهرست پروژه‌هایشان نمایش داده می‌شود.

## اجرا در توسعه
```bash
pip install -r requirements.txt
export DJANGO_DEBUG=1
python manage.py migrate
python manage.py seed_initial_data      # داده اولیه (۱۵۲ پروژه، تیم، دفاتر، گواهینامه‌ها ...)
DJANGO_SUPERUSER_USERNAME=admin DJANGO_SUPERUSER_PASSWORD=admin12345 python manage.py ensure_superuser
python manage.py runserver
```
داشبورد: `http://127.0.0.1:8000/admin/`

## تست
```bash
DJANGO_DEBUG=1 python manage.py test tests          # تست‌های واحد/یکپارچه
python tests/e2e_map.py http://127.0.0.1:8000       # تست مرورگری نقشه (نیازمند playwright و سرور در حال اجرا)
```

## ساختار
- `core/` تنظیمات سایت، استان‌ها، دفاتر، تیم، گواهینامه‌ها، پیام‌های تماس، صفحه اصلی و داشبورد
- `projects/` حوزه‌های خدمات و پروژه‌ها (+ API نقشه `/api/provinces/<slug>/`)
- `news/`، `careers/` اخبار و فرصت‌های شغلی
- `seed/` داده و تصاویر اولیه (از پروفایل شرکت)؛ `tools/build_iran_map.py` ساخت SVG استان‌ها از Natural Earth
- `DEPLOY.md` راهنمای Coolify

## نکات محتوایی
- تاریخ‌ها شمسی و به‌صورت متن ذخیره می‌شوند (`۱۴۰۱/۰۳/۲۸`).
- شماره قرارداد پروژه‌ها پیش‌فرض عمومی نیست (گزینه «نمایش شماره قرارداد» در هر پروژه).
- فونت Vazirmatn و همه فایل‌ها روی خود سرور هستند؛ هیچ CDN خارجی استفاده نمی‌شود.
