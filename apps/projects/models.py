from django.core.exceptions import ValidationError
from django.core.validators import (
    MaxValueValidator,
    MinValueValidator,
)
from django.db import models
from django.db.models import F, Q
from django.utils import timezone

from apps.core.models import TimeStampedModel


class ProjectFeature(TimeStampedModel):
    name = models.CharField(
        max_length=120,
        unique=True,
        verbose_name="نام امکان",
    )

    icon = models.CharField(
        max_length=80,
        blank=True,
        verbose_name="آیکن",
    )

    is_active = models.BooleanField(
        default=True,
        verbose_name="فعال",
    )

    display_order = models.PositiveSmallIntegerField(
        default=0,
        verbose_name="ترتیب نمایش",
    )

    class Meta:
        ordering = [
            "display_order",
            "name",
        ]
        verbose_name = "امکان پروژه"
        verbose_name_plural = "امکانات پروژه"

    def __str__(self):
        return self.name


class DevelopmentProject(TimeStampedModel):
    class ConstructionStatus(models.TextChoices):
        PLANNING = (
            "planning",
            "در مرحله برنامه‌ریزی",
        )
        UNDER_CONSTRUCTION = (
            "under_construction",
            "در حال ساخت",
        )
        COMPLETED = (
            "completed",
            "تکمیل‌شده",
        )
        ON_HOLD = (
            "on_hold",
            "متوقف‌شده",
        )

    class PublicationStatus(models.TextChoices):
        DRAFT = (
            "draft",
            "پیش‌نویس",
        )
        PENDING_REVIEW = (
            "pending_review",
            "در انتظار بررسی",
        )
        PUBLISHED = (
            "published",
            "منتشرشده",
        )
        ARCHIVED = (
            "archived",
            "بایگانی‌شده",
        )

    class Currency(models.TextChoices):
        IRT = "IRT", "تومان ایران"
        USD = "USD", "دلار آمریکا"
        EUR = "EUR", "یورو"
        AED = "AED", "درهم امارات"

    title = models.CharField(
        max_length=200,
        verbose_name="عنوان پروژه",
    )

    slug = models.SlugField(
        max_length=220,
        unique=True,
        verbose_name="نامک",
        help_text=(
            "برای آدرس صفحه پروژه، فقط از حروف انگلیسی، "
            "عدد و خط تیره استفاده شود."
        ),
    )

    reference_code = models.CharField(
        max_length=30,
        unique=True,
        verbose_name="کد پروژه",
    )

    region = models.ForeignKey(
        "locations.Region",
        on_delete=models.PROTECT,
        related_name="development_projects",
        verbose_name="منطقه",
    )

    agent = models.ForeignKey(
        "agents.Agent",
        on_delete=models.SET_NULL,
        related_name="development_projects",
        null=True,
        blank=True,
        verbose_name="مشاور مسئول",
    )

    features = models.ManyToManyField(
        ProjectFeature,
        related_name="development_projects",
        blank=True,
        verbose_name="امکانات پروژه",
    )

    construction_status = models.CharField(
        max_length=30,
        choices=ConstructionStatus.choices,
        default=ConstructionStatus.PLANNING,
        verbose_name="وضعیت ساخت",
    )

    publication_status = models.CharField(
        max_length=20,
        choices=PublicationStatus.choices,
        default=PublicationStatus.DRAFT,
        verbose_name="وضعیت انتشار",
    )

    short_description = models.CharField(
        max_length=300,
        blank=True,
        verbose_name="معرفی کوتاه",
    )

    description = models.TextField(
        verbose_name="توضیحات کامل",
    )

    public_location = models.CharField(
        max_length=250,
        blank=True,
        verbose_name="موقعیت عمومی",
        help_text=(
            "موقعیت تقریبی قابل نمایش در سایت؛ "
            "مانند اسپندکلا، محدوده جاده اصلی"
        ),
    )

    private_address = models.TextField(
        blank=True,
        verbose_name="آدرس دقیق داخلی",
        help_text=(
            "این آدرس فقط برای استفاده داخلی مجموعه است "
            "و نباید در سایت عمومی نمایش داده شود."
        ),
    )

    developer_name = models.CharField(
        max_length=150,
        blank=True,
        verbose_name="نام سازنده یا توسعه‌دهنده",
    )

    starting_price = models.DecimalField(
        max_digits=20,
        decimal_places=0,
        validators=[
            MinValueValidator(0),
        ],
        null=True,
        blank=True,
        verbose_name="قیمت شروع",
    )

    currency_code = models.CharField(
        max_length=3,
        choices=Currency.choices,
        default=Currency.IRT,
        verbose_name="واحد پول",
    )

    price_on_request = models.BooleanField(
        default=False,
        verbose_name="قیمت توافقی یا تماس بگیرید",
        help_text=(
            "با فعال‌کردن این گزینه، ثبت قیمت شروع "
            "برای انتشار الزامی نیست."
        ),
    )

    total_units = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name="تعداد کل واحدها",
    )

    available_units = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name="تعداد واحدهای موجود",
    )

    completion_percentage = models.PositiveSmallIntegerField(
        default=0,
        validators=[
            MinValueValidator(0),
            MaxValueValidator(100),
        ],
        verbose_name="درصد پیشرفت",
    )

    start_date = models.DateField(
        null=True,
        blank=True,
        verbose_name="تاریخ شروع",
    )

    expected_completion_date = models.DateField(
        null=True,
        blank=True,
        verbose_name="تاریخ تقریبی تحویل",
    )

    latitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        validators=[
            MinValueValidator(-90),
            MaxValueValidator(90),
        ],
        null=True,
        blank=True,
        verbose_name="عرض جغرافیایی",
    )

    longitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        validators=[
            MinValueValidator(-180),
            MaxValueValidator(180),
        ],
        null=True,
        blank=True,
        verbose_name="طول جغرافیایی",
    )

    is_exact_location_public = models.BooleanField(
        default=False,
        verbose_name="نمایش موقعیت دقیق در سایت",
        help_text=(
            "فقط در صورت داشتن اجازه، موقعیت دقیق "
            "پروژه در سایت عمومی نمایش داده شود."
        ),
    )

    is_featured = models.BooleanField(
        default=False,
        verbose_name="پروژه ویژه",
    )

    published_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="زمان انتشار",
    )

    class Meta:
        ordering = [
            "-published_at",
            "-created_at",
        ]

        verbose_name = "پروژه ساختمانی"
        verbose_name_plural = "پروژه‌های ساختمانی"

        indexes = [
            models.Index(
                fields=[
                    "publication_status",
                    "construction_status",
                ],
                name="project_pub_build_idx",
            ),
            models.Index(
                fields=[
                    "region",
                    "publication_status",
                ],
                name="project_region_pub_idx",
            ),
            models.Index(
                fields=[
                    "is_featured",
                    "publication_status",
                ],
                name="project_featured_pub_idx",
            ),
        ]

        constraints = [
            models.CheckConstraint(
                condition=(
                    Q(available_units__isnull=True)
                    | Q(total_units__isnull=True)
                    | Q(
                        available_units__lte=F(
                            "total_units",
                        ),
                    )
                ),
                name="project_available_units_lte_total",
            ),
            models.CheckConstraint(
                condition=(
                    Q(start_date__isnull=True)
                    | Q(
                        expected_completion_date__isnull=True,
                    )
                    | Q(
                        expected_completion_date__gte=F(
                            "start_date",
                        ),
                    )
                ),
                name="project_completion_date_gte_start",
            ),
        ]

    def __str__(self):
        return f"{self.reference_code} - {self.title}"

    def clean(self):
        """
        Validate project business rules before saving.
        """
        super().clean()

        errors = {}

        if (
            self.total_units is not None
            and self.available_units is not None
            and self.available_units > self.total_units
        ):
            errors["available_units"] = (
                "تعداد واحدهای موجود نمی‌تواند از "
                "تعداد کل واحدها بیشتر باشد."
            )

        if (
            self.start_date is not None
            and self.expected_completion_date is not None
            and self.expected_completion_date < self.start_date
        ):
            errors["expected_completion_date"] = (
                "تاریخ تقریبی تحویل نمی‌تواند "
                "قبل از تاریخ شروع پروژه باشد."
            )

        has_latitude = self.latitude is not None
        has_longitude = self.longitude is not None

        if has_latitude != has_longitude:
            errors["latitude"] = (
                "عرض و طول جغرافیایی باید هر دو باهم ثبت شوند."
            )
            errors["longitude"] = (
                "عرض و طول جغرافیایی باید هر دو باهم ثبت شوند."
            )

        if (
            self.is_exact_location_public
            and not (
                has_latitude
                and has_longitude
            )
        ):
            errors["is_exact_location_public"] = (
                "برای نمایش موقعیت دقیق، عرض و طول "
                "جغرافیایی باید ثبت شوند."
            )

        if (
            self.publication_status
            == self.PublicationStatus.PUBLISHED
            and not self.price_on_request
            and (
                self.starting_price is None
                or self.starting_price <= 0
            )
        ):
            errors["starting_price"] = (
                "برای انتشار پروژه باید قیمت شروع بیشتر "
                "از صفر ثبت شود یا گزینه «قیمت توافقی» "
                "فعال باشد."
            )

        if errors:
            raise ValidationError(errors)

    def publish(self):
        """
        Publish the project after validation.

        The project must already be saved and have a cover image.
        """
        if self.pk is None:
            raise ValidationError(
                {
                    "publication_status": (
                        "ابتدا پروژه را ذخیره و تصویر کاور "
                        "را ثبت کنید."
                    ),
                },
            )

        previous_publication_status = self.publication_status
        previous_published_at = self.published_at

        self.publication_status = (
            self.PublicationStatus.PUBLISHED
        )

        if self.published_at is None:
            self.published_at = timezone.now()

        try:
            self.full_clean()

            if not self.images.filter(
                is_cover=True,
            ).exists():
                raise ValidationError(
                    {
                        "publication_status": (
                            "برای انتشار پروژه باید یک تصویر "
                            "کاور انتخاب شود."
                        ),
                    },
                )

        except ValidationError:
            self.publication_status = (
                previous_publication_status
            )
            self.published_at = previous_published_at
            raise

        self.save(
            update_fields=[
                "publication_status",
                "published_at",
                "updated_at",
            ],
        )

    def move_to_draft(self):
        """
        Move the project back to draft status.
        """
        self.publication_status = (
            self.PublicationStatus.DRAFT
        )
        self.published_at = None

        self.save(
            update_fields=[
                "publication_status",
                "published_at",
                "updated_at",
            ],
        )

    def archive(self):
        """
        Archive the project without deleting it.
        """
        self.publication_status = (
            self.PublicationStatus.ARCHIVED
        )

        self.save(
            update_fields=[
                "publication_status",
                "updated_at",
            ],
        )


class ProjectImage(TimeStampedModel):
    project = models.ForeignKey(
        DevelopmentProject,
        on_delete=models.CASCADE,
        related_name="images",
        verbose_name="پروژه",
    )

    image = models.ImageField(
        upload_to="projects/images/",
        verbose_name="تصویر",
    )

    alt_text = models.CharField(
        max_length=200,
        blank=True,
        verbose_name="متن جایگزین تصویر",
    )

    is_cover = models.BooleanField(
        default=False,
        verbose_name="تصویر کاور",
    )

    display_order = models.PositiveSmallIntegerField(
        default=0,
        verbose_name="ترتیب نمایش",
    )

    class Meta:
        ordering = [
            "-is_cover",
            "display_order",
            "created_at",
        ]

        constraints = [
            models.UniqueConstraint(
                fields=[
                    "project",
                ],
                condition=Q(is_cover=True),
                name="unique_cover_image_per_project",
            ),
        ]

        verbose_name = "تصویر پروژه"
        verbose_name_plural = "تصاویر پروژه"

    def __str__(self):
        return f"تصویر پروژه {self.project.reference_code}"