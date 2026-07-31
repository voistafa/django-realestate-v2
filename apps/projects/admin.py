from django.contrib import admin

from .models import ProjectFeature


@admin.register(ProjectFeature)
class ProjectFeatureAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "icon",
        "is_active",
        "display_order",
    )
    list_filter = ("is_active",)
    search_fields = ("name", "icon")
    ordering = ("display_order", "name")