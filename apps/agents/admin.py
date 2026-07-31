from django.contrib import admin

from .models import Agent


@admin.register(Agent)
class AgentAdmin(admin.ModelAdmin):
    list_display = (
        "full_name",
        "job_title",
        "experience_years",
        "is_featured",
        "is_active",
        "display_order",
    )
    list_filter = ("is_active", "is_featured")
    search_fields = ("full_name", "job_title", "phone", "email")
    prepopulated_fields = {"slug": ("full_name",)}
    ordering = ("display_order", "full_name") 