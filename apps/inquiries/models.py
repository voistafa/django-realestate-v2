from django.core.validators import RegexValidator
from django.db import models

from apps.core.models import TimeStampedModel


phone_number_validator = RegexValidator(
    regex=r"^\+?[0-9۰-۹()\-\s]+$",
    message=(
        "شماره تماس فقط می‌تواند شامل عدد، فاصله، "
        "علامت +، خط تیره و پرانتز باشد."
    ),
)


class Inquiry(TimeStampedModel):
    class Status(models.TextChoices):
        NEW = "new", "جدید"
        CONTACTED = "contacted", "تماس گرفته‌شده"
        IN_PROGRESS = "in_progress", "در حال پیگیری"
        CLOSED = "closed", "بسته‌شده"
        SPAM = "spam", "هرزنامه"

    class PreferredContactMethod(models.TextChoices):
        PHONE = "phone", "تلفن"
        RUBIKA = "rubika", "روبیکا"
        EMAIL = "email", "ایمیل"

    full_name = models.CharField(
        max_length=150,
        verbose_name="نام و نام خانوادگی",
    )

    phone = models.CharField(
        max_length=30,
        validators=[
            phone_number_validator,
        ],
        verbose_name="شماره تماس",
    )

    email = models.EmailField(
        blank=True,
        verbose_name="ایمیل",
    )

    preferred_contact_method = models.CharField(
        max_length=20,
        choices=PreferredContactMethod.choices,
        default=PreferredContactMethod.PHONE,
        verbose_name="روش ارتباط ترجیحی",
    )

    property = models.ForeignKey(
        "properties.Property",
        on_delete=models.SET_NULL,
        related_name="inquiries",
        null=True,
        blank=True,
        verbose_name="ملک مرتبط",
    )

    project = models.ForeignKey(
        "projects.DevelopmentProject",
        on_delete=models.SET_NULL,
        related_name="inquiries",
        null=True,
        blank=True,
        verbose_name="پروژه مرتبط",
    )

    assigned_agent = models.ForeignKey(
        "agents.Agent",
        on_delete=models.SET_NULL,
        related_name="assigned_inquiries",
        null=True,
        blank=True,
        verbose_name="مشاور مسئول",
    )

    message = models.TextField(
        verbose_name="پیام مشتری",
    )

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.NEW,
        verbose_name="وضعیت پیگیری",
    )

    admin_notes = models.TextField(
        blank=True,
        verbose_name="یادداشت داخلی",
    )

    class Meta:
        ordering = [
            "-created_at",
        ]
        verbose_name = "درخواست مشتری"
        verbose_name_plural = "درخواست‌های مشتری"

        constraints = [
            models.CheckConstraint(
                condition=~(
                    models.Q(
                        property__isnull=False,
                    )
                    & models.Q(
                        project__isnull=False,
                    )
                ),
                name=(
                    "inquiry_cannot_target_"
                    "property_and_project"
                ),
            ),
        ]

        indexes = [
            models.Index(
                fields=[
                    "status",
                    "created_at",
                ],
                name="inquiry_status_created_idx",
            ),
            models.Index(
                fields=[
                    "phone",
                ],
                name="inquiry_phone_idx",
            ),
        ]

    def __str__(self):
        return f"{self.full_name} - {self.phone}"