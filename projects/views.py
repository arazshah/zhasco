from django.core.paginator import Paginator
from django.db.models import Count, Q
from django.http import Http404, JsonResponse
from django.shortcuts import get_object_or_404, render
from django.views.decorators.http import require_GET

from core.models import Province
from core.templatetags.zh import fa
from projects.models import Project, ServiceArea


def published():
    return Project.objects.filter(is_published=True).select_related("province", "service")


def project_list(request):
    qs = published()
    province = request.GET.get("province", "")
    service = request.GET.get("service", "")
    status = request.GET.get("status", "")
    q = request.GET.get("q", "").strip()[:100]
    if province:
        qs = qs.filter(province__slug=province)
    if service:
        qs = qs.filter(service__slug=service)
    if status in ("completed", "ongoing"):
        qs = qs.filter(status=status)
    if q:
        qs = qs.filter(Q(title__icontains=q) | Q(client__icontains=q) | Q(county__icontains=q))
    page = Paginator(qs, 18).get_page(request.GET.get("page"))
    params = request.GET.copy()
    params.pop("page", None)
    province_counts = dict(published().values_list("province__slug").annotate(n=Count("id")).values_list("province__slug", "n"))
    provinces = [p for p in Province.objects.all() if province_counts.get(p.slug)]
    for p in provinces:
        p.count = province_counts[p.slug]
    provinces.sort(key=lambda p: -p.count)
    return render(request, "projects/list.html", {
        "page": page, "total": page.paginator.count,
        "provinces": provinces, "services": ServiceArea.objects.filter(is_published=True),
        "f": {"province": province, "service": service, "status": status, "q": q},
        "querystring": params.urlencode(),
        "active_province": next((p for p in provinces if p.slug == province), None),
    })


def project_detail(request, pk):
    project = get_object_or_404(published(), pk=pk)
    related = published().filter(province=project.province).exclude(pk=pk)
    same_service = related.filter(service=project.service)[:4]
    return render(request, "projects/detail.html", {
        "p": project, "related": same_service or related[:4], "images": project.images.all(),
    })


def service_list(request):
    return render(request, "projects/services.html", {"services": ServiceArea.objects.filter(is_published=True)})


def service_detail(request, slug):
    service = get_object_or_404(ServiceArea, slug=slug, is_published=True)
    projects = published().filter(service=service)
    return render(request, "projects/service_detail.html", {
        "s": service, "projects": projects[:9], "project_count": projects.count(),
        "others": ServiceArea.objects.filter(is_published=True).exclude(pk=service.pk),
    })


@require_GET
def province_api(request, slug):
    """JSON used by the home-page map panel."""
    try:
        province = Province.objects.get(slug=slug)
    except Province.DoesNotExist:
        raise Http404
    qs = published().filter(province=province)
    items = [{
        "id": p.pk, "title": p.title, "client": p.client, "service": p.service.title,
        "service_slug": p.service.slug, "status": p.status, "end": fa(p.end_label), "url": p.get_absolute_url(),
    } for p in qs]
    resp = JsonResponse({
        "name": province.name, "slug": province.slug, "count": len(items),
        "ongoing": sum(1 for i in items if i["status"] == "ongoing"),
        "list_url": province.get_absolute_url(), "projects": items,
    }, json_dumps_params={"ensure_ascii": False})
    resp["Cache-Control"] = "public, max-age=60"
    return resp
