import jdatetime
from django.utils import timezone

from core.models import Office, SiteSettings


def site(request):
    s = SiteSettings.load()
    now = jdatetime.datetime.fromgregorian(datetime=timezone.now())
    socials = [(l, u) for l, u in [("اینستاگرام", s.instagram), ("لینکدین", s.linkedin), ("تلگرام", s.telegram),
                                   ("ایتا", s.eitaa), ("واتساپ", s.whatsapp)] if u]
    return {
        "site": s,
        "socials": socials,
        "footer_offices": list(Office.objects.all()[:4]),
        "jalali_year": now.year,
        "years_active": max(now.year - s.founded_year, 0),
    }
