from django.contrib import admin, messages
from django.utils import timezone

from .models import Agent

from apps.core.admin_fields import RubikaAdminMixin

@admin.register(Agent)
class AgentAdmin(
    RubikaAdminMixin,
    admin.ModelAdmin,
):
    list_display = (
        "full_name",
        "job_title",
        "phone",
        "experience_years",
        "is_featured",
        "is_active",
        "display_order",
    )

    list_editable = (
        "is_featured",
        "is_active",
        "display_order",
    )

    list_filter = (
        "is_active",
        "is_featured",
        "experience_years",
        "service_regions__city",
        "service_regions",
    )

    search_fields = (
        "full_name",
        "job_title",
        "specialties",
        "short_bio",
        "bio",
        "phone",
        "rubika_url",
        "email",
        "service_regions__name",
        "service_regions__city__name",
    )

    filter_horizontal = (
        "service_regions",
    )

    readonly_fields = (
        "created_at",
        "updated_at",
    )

    fieldsets = (
        (
            "اطلاعات اصلی مشاور",
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
            "تخصص و معرفی",
            {
                "fields": (
                    "specialties",
                    "short_bio",
                    "bio",
                    "experience_years",
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
                "description": (
                    "برای مشاور فعال، حداقل یکی از راه‌های ارتباطی "
                    "شامل تلفن، روبیکا یا ایمیل باید ثبت شود."
                ),
            },
        ),
        (
            "مناطق فعالیت",
            {
                "fields": (
                    "service_regions",
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
                "classes": (
                    "collapse",
                ),
            },
        ),
        (
            "تنظیمات نمایش",
            {
                "fields": (
                    (
                        "is_active",
                        "is_featured",
                    ),
                    "display_order",
                ),
            },
        ),
        (
            "اطلاعات سیستمی",
            {
                "fields": (
                    "created_at",
                    "updated_at",
                ),
                "classes": (
                    "collapse",
                ),
            },
        ),
    )

    ordering = (
        "display_order",
        "full_name",
    )

    actions = (
        "activate_selected_agents",
        "deactivate_selected_agents",
        "mark_selected_agents_as_featured",
        "remove_selected_agents_from_featured",
    )

    list_per_page = 25
    save_on_top = True

    @admin.action(
        description="فعال‌کردن مشاوران انتخاب‌شده",
    )
    def activate_selected_agents(
        self,
        request,
        queryset,
    ):
        valid_agents = []
        invalid_agents = []

        for agent in queryset:
            if agent.phone or agent.rubika_url or agent.email:
                valid_agents.append(agent.pk)
            else:
                invalid_agents.append(agent.full_name)

        updated_count = Agent.objects.filter(
            pk__in=valid_agents,
        ).update(
            is_active=True,
            updated_at=timezone.now(),
        )

        if updated_count:
            self.message_user(
                request,
                f"{updated_count} مشاور با موفقیت فعال شد.",
                level=messages.SUCCESS,
            )

        if invalid_agents:
            invalid_names = "، ".join(
                invalid_agents[:10],
            )

            self.message_user(
                request,
                (
                    "برخی مشاوران به‌دلیل نداشتن تلفن، روبیکا "
                    f"یا ایمیل فعال نشدند: {invalid_names}"
                ),
                level=messages.WARNING,
            )

    @admin.action(
        description="غیرفعال‌کردن مشاوران انتخاب‌شده",
    )
    def deactivate_selected_agents(
        self,
        request,
        queryset,
    ):
        updated_count = queryset.update(
            is_active=False,
            updated_at=timezone.now(),
        )

        self.message_user(
            request,
            f"{updated_count} مشاور غیرفعال شد.",
            level=messages.SUCCESS,
        )

    @admin.action(
        description="افزودن مشاوران انتخاب‌شده به بخش ویژه",
    )
    def mark_selected_agents_as_featured(
        self,
        request,
        queryset,
    ):
        updated_count = queryset.update(
            is_featured=True,
            updated_at=timezone.now(),
        )

        self.message_user(
            request,
            (
                f"{updated_count} مشاور "
                "به بخش مشاوران ویژه اضافه شد."
            ),
            level=messages.SUCCESS,
        )

    @admin.action(
        description="حذف مشاوران انتخاب‌شده از بخش ویژه",
    )
    def remove_selected_agents_from_featured(
        self,
        request,
        queryset,
    ):
        updated_count = queryset.update(
            is_featured=False,
            updated_at=timezone.now(),
        )

        self.message_user(
            request,
            (
                f"{updated_count} مشاور "
                "از بخش مشاوران ویژه حذف شد."
            ),
            level=messages.SUCCESS,
        )