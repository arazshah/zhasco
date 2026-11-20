from django.core.validators import FileExtensionValidator
from django.db import models
from django.urls import reverse
from django.utils import timezone

from careers.validators import validate_resume_size


class JobPosting(models.Model):
    TYPES = [("full", "تمام‌وقت"), ("part", "پاره‌وقت"), ("project", "پروژه‌ای"), ("intern", "کارآموزی")]
    title = models.CharField("عنوان شغلی", max_length=150)
    location = models.CharField("محل کار", max_length=100, default="ارومیه")
    job_type = models.CharField("نوع همکاری", max_length=10, choices=TYPES, default="full")
    description = models.TextField("شرح وظایف")
    requirements = models.TextField("شرایط و مهارت‌ها", blank=True)
    is_active = models.BooleanField("فعال", default=True)
    created_at = models.DateTimeField("تاریخ ثبت", default=timezone.now)

    class Meta:
        verbose_name = "آگهی شغلی"
        verbose_name_plural = "آگهی‌های شغلی"
        ordering = ["-created_at"]

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("careers:detail", args=[self.pk])


class JobApplication(models.Model):
    posting = models.ForeignKey(JobPosting, verbose_name="آگهی", null=True, blank=True,
                                on_delete=models.SET_NULL, related_name="applications")
    name = models.CharField("نام و نام خانوادگی", max_length=100)
    phone = models.CharField("تلفن", max_length=30)
    email = models.EmailField("ایمیل", blank=True)
    field_of_study = models.CharField("رشته و مدرک", max_length=150, blank=True)
    message = models.TextField("توضیحات", blank=True, max_length=2000)
    resume = models.FileField("رزومه", upload_to="resumes/",
                              validators=[FileExtensionValidator(["pdf", "doc", "docx"]), validate_resume_size])
    created_at = models.DateTimeField("زمان ارسال", auto_now_add=True)
    is_read = models.BooleanField("بررسی شده", default=False)
    ip = models.GenericIPAddressField("آدرس IP", null=True, blank=True)

    class Meta:
        verbose_name = "رزومه دریافتی"
        verbose_name_plural = "رزومه‌های دریافتی"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.name} — {self.posting or 'درخواست عمومی'}"
