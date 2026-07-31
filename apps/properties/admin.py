from django.contrib import admin

from .models import Feature, Property, PropertyImage, PropertyType


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


class PropertyImageInline(admin.TabularInline):
    model = PropertyImage
    extra = 1
    fields = (
        "image",
        "alt_text",
        "is_cover",
        "display_order",
    )
    ordering = ("display_order",)


@admin.register(Property)
class PropertyAdmin(admin.ModelAdmin):
    list_display = (
        "reference_code",
        "title",
        "property_type",
        "region",
        "listing_type",
        "status",
        "price",
        "currency_code",
        "is_featured",
        "published_at",
    )
    list_filter = (
        "status",
        "listing_type",
        "property_type",
        "is_featured",
        "currency_code",
    )
    search_fields = (
        "reference_code",
        "title",
        "short_description",
        "address",
        "region__name",
        "region__city__name",
        "agent__full_name",
    )
    prepopulated_fields = {"slug": ("title",)}
    autocomplete_fields = (
        "property_type",
        "region",
        "agent",
    )
    filter_horizontal = ("features",)
    list_select_related = (
        "property_type",
        "region",
        "agent",
    )
    readonly_fields = (
        "created_at",
        "updated_at",
    )
    date_hierarchy = "published_at"
    ordering = ("-published_at", "-created_at")
    inlines = (PropertyImageInline,)