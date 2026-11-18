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


# --- company mailbox ------------------------------------------------------
from django import forms  # noqa: E402
from django.contrib import messages  # noqa: E402
from django.shortcuts import redirect, render  # noqa: E402
from django.urls import path  # noqa: E402
from django.utils.html import format_html  # noqa: E402
from django.utils.safestring import mark_safe  # noqa: E402
from unfold.widgets import (UnfoldAdminEmailInputWidget, UnfoldAdminTextareaWidget,  # noqa: E402
                            UnfoldAdminTextInputWidget)

from core import mail as mailer  # noqa: E402
from core.models import MailMessage, MailSync  # noqa: E402


class ComposeForm(forms.Form):
    to = forms.CharField(label="به", widget=UnfoldAdminTextInputWidget(attrs={"dir": "ltr", "placeholder": "name@example.com"}),
                         help_text="چند گیرنده را با ویرگول جدا کنید")
    cc = forms.CharField(label="رونوشت (Cc)", required=False, widget=UnfoldAdminTextInputWidget(attrs={"dir": "ltr"}))
    subject = forms.CharField(label="موضوع", max_length=300, widget=UnfoldAdminTextInputWidget())
    body = forms.CharField(label="متن", widget=UnfoldAdminTextareaWidget(attrs={"rows": 14}))

    def clean_to(self):
        for a in [x for x in self.cleaned_data["to"].replace(";", ",").split(",") if x.strip()]:
            forms.EmailField().clean(a.strip())
        return self.cleaned_data["to"]


@admin.register(MailMessage)
class MailMessageAdmin(ModelAdmin):
    list_display = ["subject_col", "party", "when", "kind", "read_flag"]
    list_filter = ["direction", "is_read"]
    list_filter_submit = True
    search_fields = ["subject", "from_addr", "from_name", "to_addrs", "body_text"]
    actions_list = ["sync_inbox", "new_mail"]
    actions = ["mark_read", "mark_unread"]
    list_per_page = 30
    readonly_fields = ["kind", "party_full", "to_addrs", "sent_at", "attach", "body_view", "reply_link", "error"]
    fields = ["kind", "party_full", "to_addrs", "sent_at", "attach", "body_view", "error", "reply_link"]

    def has_add_permission(self, request):
        return False

    def changelist_view(self, request, extra_context=None):
        if request.method == "GET" and not request.GET and mailer.configured() and mailer.stale():
            try:
                mailer.sync_inbox()
            except mailer.MailError as exc:
                messages.warning(request, str(exc))
        elif not mailer.configured() and request.method == "GET":
            messages.warning(request, "برای فعال‌شدن ایمیل، متغیر MAIL_PASSWORD (رمز info@zhasco.ir) را در Coolify تنظیم کنید.")
        return super().changelist_view(request, extra_context)

    def change_view(self, request, object_id, form_url="", extra_context=None):
        MailMessage.objects.filter(pk=object_id, is_read=False).update(is_read=True)
        return super().change_view(request, object_id, form_url, extra_context)

    @display(description="موضوع")
    def subject_col(self, obj):
        return obj.subject or "(بدون موضوع)"

    @display(description="طرف مقابل")
    def party(self, obj):
        return obj.to_addrs if obj.direction == "out" else (obj.from_name or obj.from_addr)

    @display(description="طرف مقابل")
    def party_full(self, obj):
        return f"{obj.from_name} <{obj.from_addr}>" if obj.from_name else obj.from_addr

    @display(description="تاریخ")
    def when(self, obj):
        from core.templatetags.zh import fa, jdate
        from django.utils import timezone
        return f"{jdate(obj.sent_at, 'short')} {fa(timezone.localtime(obj.sent_at).strftime('%H:%M'))}"

    @display(description="نوع", label={"دریافتی": "info", "ارسالی": "success"})
    def kind(self, obj):
        return obj.get_direction_display()

    @display(description="وضعیت", boolean=True)
    def read_flag(self, obj):
        return obj.is_read

    @display(description="پیوست")
    def attach(self, obj):
        return "دارد (برای دیدن پیوست از وب‌میل چابکان استفاده کنید)" if obj.has_attachments else "ندارد"

    @display(description="متن ایمیل")
    def body_view(self, obj):
        if obj.body_html:
            return mark_safe(f'<div dir="auto" style="max-width:820px;line-height:1.9">{obj.body_html}</div>')
        return format_html('<pre dir="auto" style="white-space:pre-wrap;font-family:inherit;max-width:820px;line-height:1.9">{}</pre>',
                           obj.body_text)

    @display(description="اقدام")
    def reply_link(self, obj):
        if obj.direction == "in":
            return format_html('<a class="font-semibold text-primary-600" href="{}?reply={}">پاسخ دادن ←</a>',
                               reverse("admin:core_mailmessage_compose"), obj.pk)
        return "—"

    @action(description="دریافت ایمیل‌های جدید", url_path="sync-inbox", icon="sync")
    def sync_inbox(self, request):
        try:
            n = mailer.sync_inbox()
            messages.success(request, f"{n} ایمیل جدید دریافت شد." if n else "ایمیل جدیدی وجود ندارد.")
        except mailer.MailError as exc:
            messages.error(request, str(exc))
        return redirect("admin:core_mailmessage_changelist")

    @action(description="نوشتن ایمیل جدید", url_path="new-mail", icon="edit", variant="primary")
    def new_mail(self, request):
        return redirect("admin:core_mailmessage_compose")

    @admin.action(description="علامت‌گذاری به‌عنوان خوانده‌شده")
    def mark_read(self, request, queryset):
        queryset.update(is_read=True)

    @admin.action(description="علامت‌گذاری به‌عنوان خوانده‌نشده")
    def mark_unread(self, request, queryset):
        queryset.update(is_read=False)

    def get_urls(self):
        return [path("write/", self.admin_site.admin_view(self.compose_view), name="core_mailmessage_compose")] + super().get_urls()

    def compose_view(self, request):
        initial = {}
        reply = MailMessage.objects.filter(pk=request.GET.get("reply"), direction="in").first()
        if reply:
            quoted = "\n".join("> " + ln for ln in reply.body_text.splitlines()[:40])
            subj = reply.subject if reply.subject.lower().startswith("re:") else f"Re: {reply.subject}"
            initial = {"to": reply.from_addr, "subject": subj, "body": f"\n\n\n--- پیام اصلی از {reply.from_addr} ---\n{quoted}"}
        form = ComposeForm(request.POST or None, initial=initial)
        if request.method == "POST" and form.is_valid():
            d = form.cleaned_data
            try:
                mailer.send(d["to"], d["subject"], d["body"], d["cc"])
                messages.success(request, "ایمیل ارسال شد.")
                return redirect("admin:core_mailmessage_changelist")
            except mailer.MailError as exc:
                messages.error(request, str(exc))
        ctx = {**self.admin_site.each_context(request), "title": "نوشتن ایمیل", "form": form,
               "configured": mailer.configured(), "opts": self.model._meta}
        return render(request, "admin/core/mail_compose.html", ctx)
