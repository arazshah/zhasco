from django.contrib import admin
from django.db import models
from unfold.admin import ModelAdmin
from unfold.contrib.forms.widgets import WysiwygWidget

from news.models import Post


@admin.register(Post)
class PostAdmin(ModelAdmin):
    list_display = ["title", "published_at", "is_published"]
    list_editable = ["is_published"]
    search_fields = ["title", "summary"]
    list_filter = ["is_published"]
    formfield_overrides = {models.TextField: {"widget": WysiwygWidget}}
    fields = ["title", "summary", "cover", "body", "published_at", "is_published"]
