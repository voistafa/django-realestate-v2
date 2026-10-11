from django.contrib import admin

from apps.core.admin import BaseAdmin

from .models import City, Region


@admin.register(City)
class CityAdmin(BaseAdmin):
    list_display = ("name", "slug", "is_active", "created_at")
    list_filter = ("is_active",)
    search_fields = ("name", "slug")
    prepopulated_fields = {"slug": ("name",)}
    ordering = ("name",)


@admin.register(Region)
class RegionAdmin(BaseAdmin):
    list_display = ("name", "city", "slug", "is_active", "created_at")
    list_filter = ("is_active", "city")
    search_fields = ("name", "slug", "city__name")
    prepopulated_fields = {"slug": ("name",)}
    autocomplete_fields = ("city",)
    ordering = ("city__name", "name")