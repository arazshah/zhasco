from django.conf import settings
from django.contrib import admin
from django.contrib.sitemaps.views import sitemap
from django.urls import include, path, re_path
from django.views.static import serve

from core import views as core_views
from core.sitemaps import PostSitemap, ProjectSitemap, ServiceSitemap, StaticSitemap

handler404 = "core.views.not_found"
handler500 = "core.views.server_error"

sitemaps = {"static": StaticSitemap, "services": ServiceSitemap, "projects": ProjectSitemap, "news": PostSitemap}

urlpatterns = [
    path("admin/", admin.site.urls),
    path("robots.txt", core_views.robots),
    path("sitemap.xml", sitemap, {"sitemaps": sitemaps}, name="sitemap"),
    path("", include("core.urls")),
    path("", include("projects.urls")),
    path("", include("news.urls")),
    path("", include("careers.urls")),
    # Uploaded media is served by Django (small site, single container; files live on the persistent volume).
    re_path(r"^media/(?P<path>.*)$", serve, {"document_root": settings.MEDIA_ROOT}),
]
