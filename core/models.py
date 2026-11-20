from django.db import models
from django.urls import reverse


class SiteSettings(models.Model):
    """Singleton with all editable global texts and contact data."""

    company_name = models.CharField("نام شرکت", max_length=120, default="مهندسین مشاور ژرف آذران صدر")
    company_name_en = models.CharField("نام انگلیسی", max_length=120, default="Zharf Azaran Sadr Consulting Engineers")
    legal_form = models.CharField("نوع شرکت", max_length=60, default="سهامی خاص")
    registration_number = models.CharField("شماره ثبت", max_length=30, default="11803")
    founded_year = models.PositiveSmallIntegerField("سال تأسیس (شمسی)", default=1389)
    tagline = models.CharField("شعار کوتاه", max_length=200, default="مهندسی آب، خاک و اطلاعات مکانی")
    hero_title = models.CharField("عنوان صفحه اصلی", max_length=200, default="هر نقطه‌ای که رنگ دارد، پروژه‌ای در آن انجام شده است")
    hero_text = models.TextField(
        "متن صفحه اصلی", blank=True,
        default="بیش از یک دهه مطالعه، طراحی و نظارت در شبکه‌های آبیاری و زهکشی، آبخیزداری، GIS و نقشه‌برداری. "
                "روی یکی از استان‌ها کلیک کنید تا پروژه‌های انجام‌شده را ببینید.")
    about_text = models.TextField("معرفی شرکت", blank=True)
    ims_text = models.TextField("سیستم مدیریت یکپارچه (IMS)", blank=True)
    hse_text = models.TextField("خط‌مشی ایمنی، بهداشت و محیط زیست (HSE)", blank=True)
    rnd_text = models.TextField("معرفی واحد پژوهش و توسعه", blank=True)
    meta_description = models.CharField("توضیح سئو (meta description)", max_length=300, blank=True)

    email = models.EmailField("ایمیل", blank=True, default="info@zhasco.ir")
    website = models.CharField("وب‌سایت", max_length=100, blank=True, default="www.zhasco.ir")
    instagram = models.URLField("اینستاگرام", blank=True)
    linkedin = models.URLField("لینکدین", blank=True)
    telegram = models.URLField("تلگرام", blank=True)
    eitaa = models.URLField("ایتا", blank=True)
    whatsapp = models.URLField("واتساپ", blank=True)

    class Meta:
        verbose_name = "تنظیمات سایت"
        verbose_name_plural = "تنظیمات سایت"

    def __str__(self):
        return "تنظیمات سایت"

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)

    @classmethod
    def load(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj


class Province(models.Model):
    name = models.CharField("نام استان", max_length=60, unique=True)
    name_en = models.CharField("نام لاتین", max_length=60, blank=True)
    slug = models.SlugField("شناسه (لاتین)", max_length=60, unique=True)
    iso_code = models.CharField("کد ISO", max_length=10, blank=True)
    svg_path = models.TextField("مسیر SVG نقشه")
    label_x = models.FloatField("موقعیت برچسب X", default=0)
    label_y = models.FloatField("موقعیت برچسب Y", default=0)

    class Meta:
        verbose_name = "استان"
        verbose_name_plural = "استان‌ها"
        ordering = ["name"]

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return f"{reverse('projects:list')}?province={self.slug}"


class Office(models.Model):
    name = models.CharField("عنوان", max_length=80, help_text="مثلاً: دفتر مرکزی، شعبه شیراز")
    city = models.CharField("شهر", max_length=60)
    province = models.CharField("استان", max_length=60)
    is_headquarters = models.BooleanField("دفتر مرکزی", default=False)
    address = models.TextField("نشانی")
    phones = models.CharField("تلفن‌ها", max_length=200, blank=True, help_text="با ویرگول جدا کنید")
    fax = models.CharField("فکس", max_length=100, blank=True)
    email = models.EmailField("ایمیل", blank=True)
    photo = models.ImageField("تصویر", upload_to="offices/", blank=True)
    map_x = models.FloatField("موقعیت روی نقشه X", null=True, blank=True)
    map_y = models.FloatField("موقعیت روی نقشه Y", null=True, blank=True)
    order = models.PositiveSmallIntegerField("ترتیب", default=0)

    class Meta:
        verbose_name = "دفتر / شعبه"
        verbose_name_plural = "دفاتر و شعب"
        ordering = ["-is_headquarters", "order", "id"]

    def __str__(self):
        return self.name

    @property
    def phone_list(self):
        return [p.strip() for p in self.phones.split(",") if p.strip()]


class TeamMember(models.Model):
    name = models.CharField("نام و نام خانوادگی", max_length=100)
    position = models.CharField("سمت", max_length=120)
    degree = models.CharField("مدرک تحصیلی", max_length=150, blank=True)
    university = models.CharField("دانشگاه و سال اخذ مدرک", max_length=200, blank=True)
    bio = models.TextField("توضیحات", blank=True)
    photo = models.ImageField("عکس", upload_to="team/", blank=True)
    is_leadership = models.BooleanField("مدیریت ارشد", default=False)
    is_published = models.BooleanField("نمایش در سایت", default=True)
    order = models.PositiveSmallIntegerField("ترتیب", default=0)

    class Meta:
        verbose_name = "عضو تیم"
        verbose_name_plural = "اعضای تیم"
        ordering = ["order", "id"]

    def __str__(self):
        return self.name

    @property
    def initials(self):
        return "".join(w[0] for w in self.name.split()[:2])


class OrgUnit(models.Model):
    title = models.CharField("عنوان واحد / سمت", max_length=120)
    person = models.CharField("نام مسئول", max_length=120, blank=True)
    parent = models.ForeignKey("self", verbose_name="زیرمجموعهٔ", null=True, blank=True,
                               on_delete=models.CASCADE, related_name="children")
    order = models.PositiveSmallIntegerField("ترتیب", default=0)

    class Meta:
        verbose_name = "واحد سازمانی"
        verbose_name_plural = "ساختار سازمانی"
        ordering = ["order", "id"]

    def __str__(self):
        return f"{self.title}" + (f" — {self.person}" if self.person else "")


class Certificate(models.Model):
    KIND = [("iso", "گواهینامه استاندارد"), ("professional", "صلاحیت حرفه‌ای"), ("other", "سایر")]
    title = models.CharField("عنوان", max_length=150)
    code = models.CharField("کد استاندارد", max_length=40, blank=True, help_text="مثلاً ISO 9001:2015")
    issuer = models.CharField("صادرکننده", max_length=120, blank=True)
    kind = models.CharField("نوع", max_length=20, choices=KIND, default="iso")
    description = models.TextField("توضیحات", blank=True)
    image = models.ImageField("تصویر گواهینامه", upload_to="certificates/", blank=True)
    order = models.PositiveSmallIntegerField("ترتیب", default=0)
    is_published = models.BooleanField("نمایش در سایت", default=True)

    class Meta:
        verbose_name = "گواهینامه"
        verbose_name_plural = "گواهینامه‌ها"
        ordering = ["order", "id"]

    def __str__(self):
        return self.title


class Client(models.Model):
    name = models.CharField("نام کارفرما", max_length=150)
    logo = models.ImageField("لوگو", upload_to="clients/", blank=True)
    website = models.URLField("وب‌سایت", blank=True)
    order = models.PositiveSmallIntegerField("ترتیب", default=0)
    is_published = models.BooleanField("نمایش در سایت", default=True)

    class Meta:
        verbose_name = "کارفرما"
        verbose_name_plural = "کارفرمایان"
        ordering = ["order", "id"]

    def __str__(self):
        return self.name


class ValueItem(models.Model):
    KIND = [
        ("policy", "سیاست راهبردی"),
        ("goal_long", "هدف بلندمدت"),
        ("goal_mid", "هدف میان‌مدت"),
        ("goal_short", "هدف کوتاه‌مدت"),
        ("strategy", "استراتژی تحقق اهداف"),
        ("ims", "اصول سیستم مدیریت یکپارچه (IMS)"),
        ("hse", "تعهدات ایمنی، بهداشت و محیط زیست (HSE)"),
    ]
    kind = models.CharField("دسته", max_length=20, choices=KIND)
    text = models.CharField("متن", max_length=500)
    order = models.PositiveSmallIntegerField("ترتیب", default=0)

    class Meta:
        verbose_name = "سیاست / هدف"
        verbose_name_plural = "سیاست‌ها و اهداف"
        ordering = ["kind", "order", "id"]

    def __str__(self):
        return self.text[:60]


class TimelineEvent(models.Model):
    year = models.PositiveSmallIntegerField("سال (شمسی)")
    title = models.CharField("عنوان", max_length=150)
    text = models.TextField("توضیح", blank=True)

    class Meta:
        verbose_name = "رویداد تاریخچه"
        verbose_name_plural = "تاریخچه شرکت"
        ordering = ["year", "id"]

    def __str__(self):
        return f"{self.year} — {self.title}"


class RndResource(models.Model):
    title = models.CharField("عنوان", max_length=150, help_text="مثلاً: مقاله تخصصی")
    value = models.PositiveIntegerField("تعداد")
    plus = models.BooleanField("نمایش «بیش از»", default=True)
    order = models.PositiveSmallIntegerField("ترتیب", default=0)

    class Meta:
        verbose_name = "منبع پژوهشی"
        verbose_name_plural = "منابع پژوهش و توسعه"
        ordering = ["order", "id"]

    def __str__(self):
        return f"{self.value} {self.title}"


class ContactMessage(models.Model):
    name = models.CharField("نام", max_length=100)
    phone = models.CharField("تلفن", max_length=30, blank=True)
    email = models.EmailField("ایمیل", blank=True)
    subject = models.CharField("موضوع", max_length=150, blank=True)
    message = models.TextField("پیام", max_length=3000)
    created_at = models.DateTimeField("زمان ارسال", auto_now_add=True)
    is_read = models.BooleanField("خوانده شده", default=False)
    note = models.TextField("یادداشت داخلی", blank=True)
    ip = models.GenericIPAddressField("آدرس IP", null=True, blank=True)

    class Meta:
        verbose_name = "پیام تماس"
        verbose_name_plural = "پیام‌های تماس"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.name} — {self.subject or 'بدون موضوع'}"


class InitialPassword(models.Model):
    """Remembers the hash of a bootstrap password; while the user's password still equals it,
    the dashboard forces a password change (see core.middleware)."""

    user = models.OneToOneField("auth.User", on_delete=models.CASCADE, related_name="initial_password")
    password_hash = models.CharField(max_length=255)

    class Meta:
        verbose_name = "رمز اولیه"
        verbose_name_plural = "رمزهای اولیه"


class MailMessage(models.Model):
    """Local copy of mails in the company mailbox (inbox synced via IMAP, sent mail logged on send)."""

    IN, OUT = "in", "out"
    direction = models.CharField("نوع", max_length=3, choices=[("in", "دریافتی"), ("out", "ارسالی")], default="in")
    uid = models.PositiveBigIntegerField("شناسه IMAP", null=True, blank=True)
    from_name = models.CharField("نام فرستنده", max_length=200, blank=True)
    from_addr = models.CharField("ایمیل فرستنده", max_length=254, blank=True)
    to_addrs = models.CharField("گیرندگان", max_length=1000, blank=True)
    subject = models.CharField("موضوع", max_length=500, blank=True)
    body_text = models.TextField("متن", blank=True)
    body_html = models.TextField("متن (HTML پاک‌سازی‌شده)", blank=True)
    has_attachments = models.BooleanField("دارای پیوست", default=False)
    sent_at = models.DateTimeField("زمان")
    is_read = models.BooleanField("خوانده شده", default=False)
    error = models.CharField("خطای ارسال", max_length=300, blank=True)

    class Meta:
        verbose_name = "ایمیل"
        verbose_name_plural = "صندوق ایمیل"
        ordering = ["-sent_at", "-id"]
        constraints = [models.UniqueConstraint(fields=["direction", "uid"], name="uniq_mail_uid",
                                               condition=models.Q(uid__isnull=False))]

    def __str__(self):
        return self.subject or "(بدون موضوع)"


class MailSync(models.Model):
    """Singleton: state of the last IMAP sync."""

    last_sync = models.DateTimeField(null=True, blank=True)
    last_error = models.CharField(max_length=300, blank=True)

    @classmethod
    def load(cls):
        return cls.objects.get_or_create(pk=1)[0]


class MailSettings(models.Model):
    """Singleton: mailbox credentials editable from the dashboard. The password is stored encrypted
    (Fernet, key derived from SECRET_KEY) and is never shown again."""

    user = models.CharField("نشانی ایمیل (نام کاربری)", max_length=254, default="info@zhasco.ir")
    password_encrypted = models.TextField(blank=True, editable=False)
    from_name = models.CharField("نام نمایشی فرستنده", max_length=100, default="ژرف آذران صدر")
    imap_host = models.CharField("سرور دریافت (IMAP)", max_length=100, default="t1.mail.chabokan.net")
    imap_port = models.PositiveIntegerField("پورت IMAP", default=993)
    smtp_host = models.CharField("سرور ارسال (SMTP)", max_length=100, default="t1.mail.chabokan.net")
    smtp_port = models.PositiveIntegerField("پورت SMTP", default=587)

    class Meta:
        verbose_name = "تنظیمات ایمیل"
        verbose_name_plural = "تنظیمات ایمیل"

    def __str__(self):
        return "تنظیمات ایمیل"

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)

    @classmethod
    def load(cls):
        return cls.objects.get_or_create(pk=1)[0]

    @property
    def has_password(self):
        return bool(self.password_encrypted)
