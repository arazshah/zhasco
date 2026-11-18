from django.contrib import admin
from django.db import models
from unfold.admin import ModelAdmin, TabularInline
from unfold.contrib.filters.admin import ChoicesDropdownFilter, RelatedDropdownFilter
from unfold.contrib.forms.widgets import WysiwygWidget
from unfold.decorators import action, display

from projects.models import Project, ProjectImage, ServiceArea


class ProjectImageInline(TabularInline):
    model = ProjectImage
    extra = 1
    fields = ["image", "caption", "order"]


@admin.register(ServiceArea)
class ServiceAreaAdmin(ModelAdmin):
    list_display = ["title", "slug", "project_count", "is_published", "order"]
    list_editable = ["is_published", "order"]
    prepopulated_fields = {}
    formfield_overrides = {models.TextField: {"widget": WysiwygWidget}}
    fields = ["title", "slug", "icon", "summary", "image", "bullets", "body", "order", "is_published"]

    @display(description="تعداد پروژه")
    def project_count(self, obj):
        return obj.projects.count()


@admin.register(Project)
class ProjectAdmin(ModelAdmin):
    list_display = ["short_title", "province", "service", "client_short", "status_badge", "end_label", "is_featured", "is_published"]
    list_editable = ["is_featured", "is_published"]
    list_filter = [("province", RelatedDropdownFilter), ("service", RelatedDropdownFilter),
                   ("status", ChoicesDropdownFilter), "is_published", "is_featured"]
    list_filter_submit = True
    search_fields = ["title", "client", "county", "contract_number"]
    list_per_page = 30
    inlines = [ProjectImageInline]
    actions = ["publish", "unpublish"]
    fieldsets = [
        ("مشخصات اصلی", {"fields": ["title", "province", "county", "service", "client"]}),
        ("وضعیت و زمان‌بندی", {"fields": ["status", ("end_year", "end_month"), "scale"]}),
        ("قرارداد", {"fields": [("contract_number", "contract_date"), "show_contract_number"]}),
        ("توضیحات و تصویر", {"fields": ["description", "cover"]}),
        ("انتشار", {"fields": ["is_published", "is_featured"]}),
    ]

    @display(description="عنوان پروژه")
    def short_title(self, obj):
        return obj.title[:70] + ("…" if len(obj.title) > 70 else "")

    @display(description="کارفرما")
    def client_short(self, obj):
        return obj.client[:40]

    @display(description="وضعیت", label={"تکمیل‌شده": "success", "در حال اجرا": "warning"})
    def status_badge(self, obj):
        return obj.get_status_display()

    @display(description="اتمام")
    def end_label(self, obj):
        return obj.end_label

    @action(description="انتشار پروژه‌های انتخاب‌شده")
    def publish(self, request, queryset):
        queryset.update(is_published=True)

    @action(description="عدم انتشار پروژه‌های انتخاب‌شده")
    def unpublish(self, request, queryset):
        queryset.update(is_published=False)
