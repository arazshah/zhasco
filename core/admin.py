from django.contrib import admin
from django.db import models
from django.http import HttpResponseRedirect
from django.urls import reverse
from unfold.admin import ModelAdmin
from unfold.contrib.forms.widgets import WysiwygWidget
from unfold.decorators import action, display

from core.models import (Certificate, Client, ContactMessage, Office, OrgUnit, Province, RndResource,
                         SiteSettings, TeamMember, TimelineEvent, ValueItem)


@admin.register(SiteSettings)
class SiteSettingsAdmin(ModelAdmin):
    fieldsets = [
        ("هویت شرکت", {"fields": ["company_name", "company_name_en", "legal_form", "registration_number",
                                  "founded_year", "tagline", "meta_description"]}),
        ("صفحه اصلی", {"fields": ["hero_title", "hero_text"]}),
        ("متن‌های معرفی", {"fields": ["about_text", "ims_text", "hse_text", "rnd_text"]}),
        ("ارتباط و شبکه‌های اجتماعی", {"fields": ["email", "website", "instagram", "linkedin", "telegram", "eitaa", "whatsapp"]}),
    ]

    def has_add_permission(self, request):
        return not SiteSettings.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False

    def changelist_view(self, request, extra_context=None):
        obj = SiteSettings.load()
        return HttpResponseRedirect(reverse("admin:core_sitesettings_change", args=[obj.pk]))


@admin.register(Province)
class ProvinceAdmin(ModelAdmin):
    list_display = ["name", "name_en", "project_count"]
    search_fields = ["name", "name_en"]
    fields = ["name", "name_en", "slug", "iso_code", "label_x", "label_y"]
    list_per_page = 40

    @display(description="تعداد پروژه منتشرشده")
    def project_count(self, obj):
        return obj.projects.filter(is_published=True).count()

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(Office)
class OfficeAdmin(ModelAdmin):
    list_display = ["name", "city", "province", "is_headquarters", "order"]
    list_editable = ["order"]
    fieldsets = [
        (None, {"fields": ["name", "city", "province", "is_headquarters", "address", "phones", "fax", "email", "photo", "order"]}),
        ("موقعیت روی نقشه صفحه اصلی (اختیاری)", {"fields": ["map_x", "map_y"], "classes": ["collapse"]}),
    ]


@admin.register(TeamMember)
class TeamMemberAdmin(ModelAdmin):
    list_display = ["name", "position", "degree", "is_leadership", "is_published", "order"]
    list_editable = ["is_leadership", "is_published", "order"]
    search_fields = ["name", "position"]


@admin.register(OrgUnit)
class OrgUnitAdmin(ModelAdmin):
    list_display = ["title", "person", "parent", "order"]
    list_editable = ["order"]
    list_filter = ["parent"]
    search_fields = ["title", "person"]


@admin.register(Certificate)
class CertificateAdmin(ModelAdmin):
    list_display = ["title", "code", "kind", "is_published", "order"]
    list_editable = ["is_published", "order"]


@admin.register(Client)
class ClientAdmin(ModelAdmin):
    list_display = ["name", "is_published", "order"]
    list_editable = ["is_published", "order"]
    search_fields = ["name"]


@admin.register(ValueItem)
class ValueItemAdmin(ModelAdmin):
    list_display = ["text", "kind", "order"]
    list_editable = ["order"]
    list_filter = ["kind"]
    search_fields = ["text"]


@admin.register(TimelineEvent)
class TimelineEventAdmin(ModelAdmin):
    list_display = ["year", "title"]


@admin.register(RndResource)
class RndResourceAdmin(ModelAdmin):
    list_display = ["title", "value", "plus", "order"]
    list_editable = ["value", "plus", "order"]


@admin.register(ContactMessage)
class ContactMessageAdmin(ModelAdmin):
    list_display = ["name", "subject", "phone", "email", "created_display", "is_read"]
    list_filter = ["is_read"]
    search_fields = ["name", "subject", "message", "phone", "email"]
    readonly_fields = ["name", "phone", "email", "subject", "message", "created_at"]
    fields = ["name", "phone", "email", "subject", "message", "created_at", "is_read", "note"]
    actions = ["mark_read"]

    def has_add_permission(self, request):
        return False

    @display(description="زمان")
    def created_display(self, obj):
        from core.templatetags.zh import jdate
        return jdate(obj.created_at, "short")

    @action(description="علامت‌گذاری به‌عنوان خوانده‌شده")
    def mark_read(self, request, queryset):
        queryset.update(is_read=True)
