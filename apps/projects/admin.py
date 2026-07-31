from django.contrib import admin

from .models import DevelopmentProject, ProjectFeature, ProjectImage


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


class ProjectImageInline(admin.TabularInline):
    model = ProjectImage
    extra = 1
    fields = (
        "image",
        "alt_text",
        "is_cover",
        "display_order",
    )
    ordering = ("display_order",)


@admin.register(DevelopmentProject)
class DevelopmentProjectAdmin(admin.ModelAdmin):
    list_display = (
        "reference_code",
        "title",
        "region",
        "status",
        "completion_percentage",
        "starting_price",
        "currency_code",
        "is_featured",
        "published_at",
    )
    list_filter = (
        "status",
        "is_featured",
        "currency_code",
        "region__city",
    )
    search_fields = (
        "reference_code",
        "title",
        "developer_name",
        "short_description",
        "address",
        "region__name",
        "region__city__name",
        "agent__full_name",
    )
    prepopulated_fields = {"slug": ("title",)}
    autocomplete_fields = (
        "region",
        "agent",
    )
    filter_horizontal = ("features",)
    list_select_related = (
        "region",
        "agent",
    )
    readonly_fields = (
        "created_at",
        "updated_at",
    )
    date_hierarchy = "published_at"
    ordering = ("-published_at", "-created_at")
    inlines = (ProjectImageInline,)