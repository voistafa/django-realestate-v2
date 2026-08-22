from django.core.exceptions import ValidationError
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


class OrganizationMember(TimeStampedModel):
    full_name = models.CharField(
        max_length=150,
        verbose_name="نام و نام خانوادگی",
    )

    slug = models.SlugField(
        max_length=170,
        unique=True,
        verbose_name="نامک",
    )

    job_title = models.CharField(
        max_length=120,
        verbose_name="سمت",
    )

    photo = models.ImageField(
        upload_to="organization/photos/",
        blank=True,
        verbose_name="تصویر",
    )

    phone = models.CharField(
        max_length=30,
        blank=True,
        validators=[phone_number_validator],
        verbose_name="شماره تماس",
    )

    rubika_url = models.CharField(
    max_length=255,
    blank=True,
    verbose_name="روبیکا",
    help_text="آیدی یا لینک روبیکا را وارد کنید.",
)

    email = models.EmailField(
        blank=True,
        verbose_name="ایمیل",
    )

    short_bio = models.CharField(
        max_length=250,
        blank=True,
        verbose_name="معرفی کوتاه",
    )

    bio = models.TextField(
        blank=True,
        verbose_name="معرفی کامل",
    )

    instagram_url = models.URLField(
        blank=True,
        verbose_name="اینستاگرام",
    )

    linkedin_url = models.URLField(
        blank=True,
        verbose_name="لینکدین",
    )

    is_active = models.BooleanField(
        default=True,
        verbose_name="فعال",
    )

    is_primary_manager = models.BooleanField(
        default=False,
        verbose_name="مدیر اصلی",
        help_text="فقط یک عضو می‌تواند به‌عنوان مدیر اصلی سایت انتخاب شود.",
    )

    display_order = models.PositiveSmallIntegerField(
        default=0,
        verbose_name="ترتیب نمایش",
    )

    class Meta:
        ordering = [
            "display_order",
            "full_name",
        ]

        verbose_name = "عضو مجموعه"
        verbose_name_plural = "اعضای مجموعه"

        constraints = [
            models.UniqueConstraint(
                fields=["is_primary_manager"],
                condition=models.Q(is_primary_manager=True),
                name="unique_primary_organization_manager",
            ),
        ]

    def __str__(self):
        return f"{self.full_name} - {self.job_title}"

    def clean(self):
        super().clean()

        if (
            self.is_active
            and not self.phone
            and not self.rubika_url
            and not self.email
        ):
            raise ValidationError(
                {
                    "phone": (
                        "برای عضو فعال، حداقل یک راه ارتباطی "
                        "شامل تلفن، روبیکا یا ایمیل ثبت شود."
                    )
                }
            )

        if self.is_primary_manager and not self.is_active:
            raise ValidationError(
                {
                    "is_primary_manager": (
                        "مدیر اصلی سایت باید در وضعیت فعال باشد."
                    )
                }
            )

        if self.is_primary_manager and not self.phone:
            raise ValidationError(
                {
                    "phone": (
                        "ثبت شماره تماس برای مدیر اصلی سایت الزامی است."
                    )
                }
            )

        if self.is_primary_manager:
            existing_manager = OrganizationMember.objects.filter(
                is_primary_manager=True,
            )

            if self.pk:
                existing_manager = existing_manager.exclude(pk=self.pk)

            if existing_manager.exists():
                raise ValidationError(
                    {
                        "is_primary_manager": (
                            "یک مدیر اصلی قبلاً برای سایت انتخاب شده است."
                        )
                    }
                )