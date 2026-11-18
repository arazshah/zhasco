from django.core.validators import RegexValidator
from django.db import models
from django.urls import reverse

JALALI_DATE = RegexValidator(r"^1[34]\d{2}/(0[1-9]|1[0-2])/(0[1-9]|[12]\d|3[01])$",
                             "تاریخ را به شکل ۱۴۰۱/۰۳/۲۸ (شمسی) وارد کنید.")

MONTHS = [(1, "فروردین"), (2, "اردیبهشت"), (3, "خرداد"), (4, "تیر"), (5, "مرداد"), (6, "شهریور"),
          (7, "مهر"), (8, "آبان"), (9, "آذر"), (10, "دی"), (11, "بهمن"), (12, "اسفند")]

ICONS = [
    ("irrigation", "آبیاری"), ("drainage", "زهکشی و آب"), ("watershed", "آبخیزداری و کوهستان"),
    ("agriculture", "کشاورزی"), ("gis", "GIS و نقشه"), ("survey", "نقشه‌برداری"),
    ("green", "فضای سبز و محیط زیست"),
]


class ServiceArea(models.Model):
    slug = models.SlugField("شناسه (لاتین)", max_length=40, unique=True)
    title = models.CharField("عنوان", max_length=120)
    summary = models.CharField("خلاصه", max_length=300, blank=True)
    body = models.TextField("توضیحات کامل", blank=True, help_text="می‌توانید از قالب‌بندی متن استفاده کنید.")
    bullets = models.TextField("فهرست خدمات", blank=True, help_text="هر خدمت در یک خط")
    icon = models.CharField("آیکون", max_length=20, choices=ICONS, default="irrigation")
    image = models.ImageField("تصویر", upload_to="services/", blank=True)
    order = models.PositiveSmallIntegerField("ترتیب", default=0)
    is_published = models.BooleanField("نمایش در سایت", default=True)

    class Meta:
        verbose_name = "حوزه خدمات"
        verbose_name_plural = "حوزه‌های خدمات"
        ordering = ["order", "id"]

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("projects:service_detail", args=[self.slug])

    @property
    def bullet_list(self):
        return [b.strip() for b in self.bullets.splitlines() if b.strip()]


class Project(models.Model):
    STATUS = [("completed", "تکمیل‌شده"), ("ongoing", "در حال اجرا")]

    title = models.CharField("عنوان پروژه", max_length=400)
    province = models.ForeignKey("core.Province", verbose_name="استان", on_delete=models.PROTECT, related_name="projects")
    county = models.CharField("شهرستان", max_length=80, blank=True)
    service = models.ForeignKey(ServiceArea, verbose_name="حوزه خدمات", on_delete=models.PROTECT, related_name="projects")
    client = models.CharField("کارفرما", max_length=200)
    status = models.CharField("وضعیت", max_length=12, choices=STATUS, default="completed")
    contract_number = models.CharField("شماره قرارداد", max_length=60, blank=True)
    contract_date = models.CharField("تاریخ قرارداد (شمسی)", max_length=10, blank=True, validators=[JALALI_DATE],
                                     help_text="مثال: ۱۴۰۱/۰۳/۲۸")
    end_year = models.PositiveSmallIntegerField("سال اتمام (شمسی)", null=True, blank=True)
    end_month = models.PositiveSmallIntegerField("ماه اتمام", choices=MONTHS, null=True, blank=True)
    scale = models.CharField("مقیاس پروژه", max_length=80, blank=True, help_text="مثلاً ۴۰۰۰ هکتار یا ۱۴۴ کیلومتر")
    description = models.TextField("توضیحات", blank=True)
    cover = models.ImageField("تصویر شاخص", upload_to="projects/", blank=True)
    is_featured = models.BooleanField("پروژه شاخص (نمایش در صفحه اصلی)", default=False)
    show_contract_number = models.BooleanField("نمایش شماره قرارداد در سایت", default=False)
    is_published = models.BooleanField("منتشر شده", default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "پروژه"
        verbose_name_plural = "پروژه‌ها"
        ordering = ["-status", "-end_year", "-end_month", "-id"]
        indexes = [models.Index(fields=["is_published", "province"])]

    def __str__(self):
        return self.title[:80]

    def get_absolute_url(self):
        return reverse("projects:detail", args=[self.pk])

    @property
    def end_label(self):
        if self.status == "ongoing":
            return "در حال اجرا"
        if self.end_year:
            m = dict(MONTHS).get(self.end_month)
            return f"{m} {self.end_year}" if m else str(self.end_year)
        return ""


class ProjectImage(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="images")
    image = models.ImageField("تصویر", upload_to="projects/gallery/")
    caption = models.CharField("شرح", max_length=200, blank=True)
    order = models.PositiveSmallIntegerField("ترتیب", default=0)

    class Meta:
        verbose_name = "تصویر پروژه"
        verbose_name_plural = "تصاویر پروژه"
        ordering = ["order", "id"]
