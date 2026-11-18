from django.contrib.sitemaps import Sitemap
from django.urls import reverse

from news.models import Post
from projects.models import Project, ServiceArea


class StaticSitemap(Sitemap):
    priority = 0.7
    changefreq = "monthly"

    def items(self):
        return ["core:home", "core:about", "core:team", "core:quality", "core:rnd", "core:contact",
                "projects:list", "projects:services", "news:list", "careers:list"]

    def location(self, item):
        return reverse(item)


class ProjectSitemap(Sitemap):
    priority = 0.6

    def items(self):
        return Project.objects.filter(is_published=True)

    def lastmod(self, obj):
        return obj.updated_at


class ServiceSitemap(Sitemap):
    priority = 0.8

    def items(self):
        return ServiceArea.objects.filter(is_published=True)


class PostSitemap(Sitemap):
    priority = 0.5

    def items(self):
        return Post.objects.filter(is_published=True)

    def lastmod(self, obj):
        return obj.published_at
