from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, RegexValidator
from django.db import models

from apps.core.models import TimeStampedModel


phone_number_validator = RegexValidator(
    regex=r"^\+?[0-9۰-۹()\-\s]+$",
    message=(
        "شماره تماس فقط می‌تواند شامل عدد، فاصله، "
        "علامت +، خط تیره و پرانتز باشد."
    ),
)


class Agent(TimeStampedModel):
    full_name = models.CharField(
        max_length=150,
        verbose_name="نام و نام خانوادگی",
    )

    slug = models.SlugField(
        max_length=170,
        unique=True,
        verbose_name="نامک",
        help_text="برای آدرس صفحه مشاور، فقط از حروف انگلیسی استفاده شود.",
    )

    job_title = models.CharField(
        max_length=120,
        blank=True,
        verbose_name="عنوان شغلی",
    )

    specialties = models.CharField(
        max_length=250,
        blank=True,
        verbose_name="تخصص‌ها",
        help_text="مثال: خرید و فروش ویلا، زمین و پروژه‌های ساختمانی",
    )

    short_bio = models.CharField(
        max_length=250,
        blank=True,
        verbose_name="معرفی کوتاه",
        help_text="متن کوتاه برای نمایش در کارت مشاور",
    )

    bio = models.TextField(
        blank=True,
        verbose_name="معرفی کامل",
    )

    photo = models.ImageField(
        upload_to="agents/photos/",
        blank=True,
        verbose_name="تصویر مشاور",
    )

    phone = models.CharField(
        max_length=30,
        blank=True,
        validators=[phone_number_validator],
        verbose_name="شماره تماس",
    )

    rubika_url = models.URLField(
        blank=True,
        verbose_name="لینک روبیکا",
        help_text="مثال: https://rubika.ir/username",
    )

    email = models.EmailField(
        blank=True,
        verbose_name="ایمیل",
    )

    service_regions = models.ManyToManyField(
        "locations.Region",
        related_name="agents",
        blank=True,
        verbose_name="مناطق فعالیت",
    )

    experience_years = models.PositiveSmallIntegerField(
        default=0,
        validators=[MinValueValidator(0)],
        verbose_name="سابقه کاری",
        help_text="تعداد سال‌های سابقه فعالیت",
    )

    instagram_url = models.URLField(
        blank=True,
        verbose_name="لینک اینستاگرام",
    )

    linkedin_url = models.URLField(
        blank=True,
        verbose_name="لینک لینکدین",
    )

    is_featured = models.BooleanField(
        default=False,
        verbose_name="مشاور ویژه",
    )

    is_active = models.BooleanField(
        default=True,
        verbose_name="فعال",
        help_text="مشاور فعال در بخش عمومی سایت قابل نمایش است.",
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
        verbose_name = "مشاور"
        verbose_name_plural = "مشاوران"

    def __str__(self):
        return self.full_name

    def clean(self):
        """
        Validate the public contact information of active agents.
        """
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
                        "برای مشاور فعال، حداقل یکی از راه‌های ارتباطی "
                        "شامل تلفن، روبیکا یا ایمیل باید ثبت شود."
                    ),
                },
            )