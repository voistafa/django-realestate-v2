from django.contrib import admin

from .models import OrganizationMember

from apps.core.admin_fields import RubikaAdminMixin

@admin.register(OrganizationMember)
class OrganizationMemberAdmin(
    RubikaAdminMixin,
    admin.ModelAdmin,
):
    list_display = (
        "full_name",
        "job_title",
        "phone",
        "is_primary_manager",
        "is_active",
        "display_order",
    )

    list_editable = (
        "is_active",
        "display_order",
    )

    list_filter = (
        "is_primary_manager",
        "is_active",
    )

    search_fields = (
        "full_name",
        "job_title",
        "phone",
        "email",
    )

    prepopulated_fields = {
        "slug": ("full_name",),
    }

    readonly_fields = (
        "created_at",
        "updated_at",
    )

    fieldsets = (
        (
            "اطلاعات اصلی",
            {
                "fields": (
                    "full_name",
                    "slug",
                    "job_title",
                    "photo",
                ),
            },
        ),
        (
            "مدیریت و نمایش",
            {
                "fields": (
                    "is_primary_manager",
                    "is_active",
                    "display_order",
                ),
            },
        ),
        (
            "راه‌های ارتباطی",
            {
                "fields": (
                    "phone",
                    "rubika_url",
                    "email",
                ),
            },
        ),
        (
            "معرفی",
            {
                "fields": (
                    "short_bio",
                    "bio",
                ),
            },
        ),
        (
            "شبکه‌های اجتماعی",
            {
                "fields": (
                    "instagram_url",
                    "linkedin_url",
                ),
                "classes": ("collapse",),
            },
        ),
        (
            "اطلاعات سیستمی",
            {
                "fields": (
                    "created_at",
                    "updated_at",
                ),
                "classes": ("collapse",),
            },
        ),
    )

    ordering = (
        "-is_primary_manager",
        "display_order",
        "full_name",
    )

    save_on_top = True