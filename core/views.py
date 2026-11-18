import time

from django.contrib import messages
from django.db.models import Count, Q
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.views.decorators.http import require_http_methods, require_GET

from core import map_data
from core.forms import ContactForm
from core.models import (Certificate, Client, Office, OrgUnit, Province, RndResource, TeamMember,
                         TimelineEvent, ValueItem)
from news.models import Post
from projects.models import Project, ServiceArea


def home(request):
    published = Project.objects.filter(is_published=True)
    counts = dict(published.values_list("province_id").annotate(n=Count("id")).values_list("province_id", "n"))
    provinces = list(Province.objects.all())
    for p in provinces:
        p.count = counts.get(p.id, 0)
    active = [p for p in provinces if p.count]
    ctx = {
        "provinces": provinces,
        "map_meta": map_data.meta(),
        "offices": Office.objects.exclude(map_x=None),
        "stats": {
            "projects": published.count(),
            "provinces": len(active),
            "ongoing": published.filter(status="ongoing").count(),
        },
        "active_provinces": sorted(active, key=lambda p: -p.count),
        "services": ServiceArea.objects.filter(is_published=True),
        "featured": published.filter(is_featured=True).select_related("province", "service")[:6],
        "certificates": Certificate.objects.filter(is_published=True, kind="iso"),
        "clients": Client.objects.filter(is_published=True),
        "latest_posts": Post.objects.filter(is_published=True)[:3],
    }
    return render(request, "core/home.html", ctx)


def about(request):
    values = {}
    for v in ValueItem.objects.all():
        values.setdefault(v.kind, []).append(v)
    roots = OrgUnit.objects.filter(parent=None).prefetch_related("children__children")
    return render(request, "core/about.html", {
        "values": values,
        "timeline": TimelineEvent.objects.all(),
        "org_roots": roots,
        "org_has_data": roots.exists(),
    })


def team(request):
    members = TeamMember.objects.filter(is_published=True)
    return render(request, "core/team.html", {
        "leaders": [m for m in members if m.is_leadership],
        "members": [m for m in members if not m.is_leadership],
    })


def quality(request):
    values = {}
    for v in ValueItem.objects.filter(kind__in=["ims", "hse"]):
        values.setdefault(v.kind, []).append(v)
    return render(request, "core/quality.html", {
        "certificates": Certificate.objects.filter(is_published=True),
        "values": values,
    })


def rnd(request):
    return render(request, "core/rnd.html", {"resources": RndResource.objects.all()})


@require_http_methods(["GET", "POST"])
def contact(request):
    form = ContactForm(request.POST or None)
    if request.method == "POST":
        last = request.session.get("last_contact", 0)
        if time.time() - last < 20:
            messages.error(request, "لطفاً چند ثانیه بعد دوباره تلاش کنید.")
        elif form.is_valid():
            form.save()
            request.session["last_contact"] = time.time()
            messages.success(request, "پیام شما ثبت شد. در اسرع وقت با شما تماس می‌گیریم.")
            return redirect("core:contact")
        elif form.errors.get("__all__") == ["spam"]:
            return redirect("core:contact")
    return render(request, "core/contact.html", {"form": form, "offices": Office.objects.all()})


@require_GET
def robots(request):
    body = "User-agent: *\nDisallow: /admin/\nDisallow: /api/\nSitemap: %s\n" % request.build_absolute_uri("/sitemap.xml")
    return HttpResponse(body, content_type="text/plain")


def not_found(request, exception=None):
    return render(request, "404.html", status=404)


def server_error(request):
    return render(request, "500.html", status=500)
