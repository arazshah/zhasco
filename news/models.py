from django.db import models
from django.urls import reverse
from django.utils import timezone


class Post(models.Model):
    title = models.CharField("عنوان", max_length=250)
    summary = models.CharField("خلاصه", max_length=400, blank=True)
    body = models.TextField("متن")
    cover = models.ImageField("تصویر شاخص", upload_to="news/", blank=True)
    published_at = models.DateTimeField("زمان انتشار", default=timezone.now)
    is_published = models.BooleanField("منتشر شده", default=True)

    class Meta:
        verbose_name = "خبر / مقاله"
        verbose_name_plural = "اخبار و مقالات"
        ordering = ["-published_at", "-id"]

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("news:detail", args=[self.pk])
