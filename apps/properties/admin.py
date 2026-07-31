from django.contrib import admin

from .models import Feature, PropertyType


@admin.register(PropertyType)
class PropertyTypeAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "slug",
        "is_active",
        "display_order",
    )
    list_filter = ("is_active",)
    search_fields = ("name", "slug")
    prepopulated_fields = {"slug": ("name",)}
    ordering = ("display_order", "name")


@admin.register(Feature)
class FeatureAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "icon",
        "is_active",
        "display_order",
    )
    list_filter = ("is_active",)
    search_fields = ("name", "icon")
    ordering = ("display_order", "name")