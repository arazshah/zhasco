from django.db.models import Count

from careers.models import JobApplication
from core.models import ContactMessage, Province
from news.models import Post
from projects.models import Project


def unread_messages_badge(request):
    n = ContactMessage.objects.filter(is_read=False).count()
    return str(n) if n else None


def unread_applications_badge(request):
    n = JobApplication.objects.filter(is_read=False).count()
    return str(n) if n else None


def dashboard_callback(request, context):
    projects = Project.objects.all()
    by_province = list(
        Province.objects.annotate(n=Count("projects")).filter(n__gt=0).order_by("-n").values("name", "n"))
    top = by_province[0]["n"] if by_province else 1
    for row in by_province:
        row["pct"] = round(row["n"] * 100 / top)
    by_service = list(
        projects.values("service__title").annotate(n=Count("id")).order_by("-n").values("service__title", "n"))
    context.update({
        "kpis": [
            {"label": "پروژه‌های منتشرشده", "value": projects.filter(is_published=True).count(), "icon": "engineering"},
            {"label": "در حال اجرا", "value": projects.filter(status="ongoing", is_published=True).count(), "icon": "autorenew"},
            {"label": "استان‌های رنگی نقشه", "value": len(by_province), "icon": "map"},
            {"label": "پیام‌های خوانده‌نشده", "value": ContactMessage.objects.filter(is_read=False).count(), "icon": "mail"},
            {"label": "رزومه‌های جدید", "value": JobApplication.objects.filter(is_read=False).count(), "icon": "description"},
            {"label": "اخبار منتشرشده", "value": Post.objects.filter(is_published=True).count(), "icon": "newspaper"},
        ],
        "by_province": by_province,
        "by_service": by_service,
        "recent_messages": ContactMessage.objects.all()[:5],
        "recent_applications": JobApplication.objects.select_related("posting")[:5],
        "unpublished": projects.filter(is_published=False).count(),
    })
    return context
