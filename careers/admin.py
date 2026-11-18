from django.contrib import admin
from django.db import models
from unfold.admin import ModelAdmin
from unfold.contrib.forms.widgets import WysiwygWidget
from unfold.decorators import action, display

from careers.models import JobApplication, JobPosting


@admin.register(JobPosting)
class JobPostingAdmin(ModelAdmin):
    list_display = ["title", "location", "job_type", "is_active", "application_count"]
    list_editable = ["is_active"]
    formfield_overrides = {models.TextField: {"widget": WysiwygWidget}}

    @display(description="رزومه‌ها")
    def application_count(self, obj):
        return obj.applications.count()


@admin.register(JobApplication)
class JobApplicationAdmin(ModelAdmin):
    list_display = ["name", "posting", "phone", "email", "created_display", "is_read"]
    list_filter = ["is_read", "posting"]
    search_fields = ["name", "phone", "email", "field_of_study"]
    readonly_fields = ["posting", "name", "phone", "email", "field_of_study", "message", "resume", "created_at"]
    fields = ["posting", "name", "phone", "email", "field_of_study", "message", "resume", "created_at", "is_read"]
    actions = ["mark_read"]

    def has_add_permission(self, request):
        return False

    @display(description="زمان")
    def created_display(self, obj):
        from core.templatetags.zh import jdate
        return jdate(obj.created_at, "short")

    @action(description="علامت‌گذاری به‌عنوان بررسی‌شده")
    def mark_read(self, request, queryset):
        queryset.update(is_read=True)
