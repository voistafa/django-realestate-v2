from django.contrib import admin

from .models import Inquiry


@admin.register(Inquiry)
class InquiryAdmin(admin.ModelAdmin):
    list_display = (
        "full_name",
        "phone",
        "preferred_contact_method",
        "status",
        "property",
        "project",
        "assigned_agent",
        "created_at",
    )
    list_filter = (
        "status",
        "preferred_contact_method",
        "created_at",
    )
    search_fields = (
        "full_name",
        "phone",
        "email",
        "message",
        "property__title",
        "project__title",
        "assigned_agent__full_name",
    )
    autocomplete_fields = (
        "property",
        "project",
        "assigned_agent",
    )
    readonly_fields = (
        "created_at",
        "updated_at",
    )
    list_select_related = (
        "property",
        "project",
        "assigned_agent",
    )
    date_hierarchy = "created_at"
    ordering = ("-created_at",)