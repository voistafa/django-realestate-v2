from django.core.exceptions import ValidationError
from django.core.validators import (
    MaxValueValidator,
    MinValueValidator,
    RegexValidator,
)
from django.db import models
from django.db.models import F, Q
from django.utils import timezone

from apps.core.models import TimeStampedModel


phone_number_validator = RegexValidator(
    regex=r"^\+?[0-9۰-۹()\-\s]+$",
    message=(
        "شماره تماس فقط می‌تواند شامل عدد، فاصله، "
        "علامت +، خط تیره و پرانتز باشد."
    ),
)


class PropertyType(TimeStampedModel):
    name = models.CharField(
        max_length=100,
        unique=True,
        verbose_name="نام نوع ملک",
    )

    slug = models.SlugField(
        max_length=120,
        unique=True,
        verbose_name="نامک",
        help_text=(
            "برای آدرس صفحه نوع ملک، از حروف انگلیسی، "
            "عدد و خط تیره استفاده شود."
        ),
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
        verbose_name = "نوع ملک"
        verbose_name_plural = "انواع ملک"

    def __str__(self):
        return self.name


class Feature(TimeStampedModel):
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
        verbose_name = "امکان ملک"
        verbose_name_plural = "امکانات ملک"

    def __str__(self):
        return self.name


class Property(TimeStampedModel):
    class TransactionType(models.TextChoices):
        SALE = "sale", "فروش"
        RENT = "rent", "اجاره"
        MORTGAGE_RENT = (
            "mortgage_rent",
            "رهن و اجاره",
        )
        FULL_MORTGAGE = (
            "full_mortgage",
            "رهن کامل",
        )
        PRE_SALE = "pre_sale", "پیش‌فروش"

    class PublicationStatus(models.TextChoices):
        DRAFT = "draft", "پیش‌نویس"
        PENDING_REVIEW = (
            "pending_review",
            "در انتظار بررسی",
        )
        PUBLISHED = "published", "منتشرشده"
        ARCHIVED = "archived", "بایگانی‌شده"

    class AvailabilityStatus(models.TextChoices):
        AVAILABLE = "available", "موجود"
        RESERVED = "reserved", "رزروشده"
        SOLD = "sold", "فروخته‌شده"
        RENTED = "rented", "اجاره‌رفته"
        UNAVAILABLE = (
            "unavailable",
            "موقتاً غیرفعال",
        )

    class Currency(models.TextChoices):
        IRT = "IRT", "تومان ایران"
        USD = "USD", "دلار آمریکا"
        EUR = "EUR", "یورو"
        AED = "AED", "درهم امارات"

    class DeedType(models.TextChoices):
        OFFICIAL_SINGLE_PAGE = (
            "official_single_page",
            "سند رسمی تک‌برگ",
        )
        OFFICIAL_BOOKLET = (
            "official_booklet",
            "سند رسمی دفترچه‌ای",
        )
        CONTRACTUAL = "contractual", "قولنامه‌ای"
        COOPERATIVE = "cooperative", "تعاونی"
        LEASEHOLD = (
            "leasehold",
            "حق بهره‌برداری یا اجاره بلندمدت",
        )
        IN_PROGRESS = (
            "in_progress",
            "سند در حال اقدام",
        )
        UNKNOWN = "unknown", "نامشخص"

    title = models.CharField(
        max_length=200,
        verbose_name="عنوان ملک",
    )

    slug = models.SlugField(
        max_length=220,
        unique=True,
        verbose_name="نامک",
        help_text=(
            "برای آدرس صفحه ملک، از حروف انگلیسی، "
            "عدد و خط تیره استفاده شود."
        ),
    )

    reference_code = models.CharField(
        max_length=30,
        unique=True,
        verbose_name="کد ملک",
    )

    property_type = models.ForeignKey(
        PropertyType,
        on_delete=models.PROTECT,
        related_name="properties",
        verbose_name="نوع ملک",
    )

    region = models.ForeignKey(
        "locations.Region",
        on_delete=models.PROTECT,
        related_name="properties",
        verbose_name="منطقه",
    )

    project = models.ForeignKey(
        "projects.DevelopmentProject",
        on_delete=models.SET_NULL,
        related_name="properties",
        null=True,
        blank=True,
        verbose_name="پروژه ساختمانی",
        help_text=(
            "این فیلد فقط برای املاک و واحدهای "
            "وابسته به یک پروژه انتخاب شود."
        ),
    )

    agent = models.ForeignKey(
        "agents.Agent",
        on_delete=models.SET_NULL,
        related_name="properties",
        null=True,
        blank=True,
        verbose_name="مشاور مسئول",
    )

    features = models.ManyToManyField(
        Feature,
        related_name="properties",
        blank=True,
        verbose_name="امکانات ملک",
    )

    transaction_type = models.CharField(
        max_length=20,
        choices=TransactionType.choices,
        default=TransactionType.SALE,
        verbose_name="نوع معامله",
    )

    publication_status = models.CharField(
        max_length=20,
        choices=PublicationStatus.choices,
        default=PublicationStatus.DRAFT,
        verbose_name="وضعیت انتشار",
    )

    availability_status = models.CharField(
        max_length=20,
        choices=AvailabilityStatus.choices,
        default=AvailabilityStatus.AVAILABLE,
        verbose_name="وضعیت دسترسی",
    )

    short_description = models.CharField(
        max_length=300,
        blank=True,
        verbose_name="توضیح کوتاه",
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

    latitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        validators=[
            MinValueValidator(-90),
            MaxValueValidator(90),
        ],
        null=True,
        blank=True,
        verbose_name="عرض جغرافیایی عمومی",
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
        verbose_name="طول جغرافیایی عمومی",
    )

    is_exact_location_public = models.BooleanField(
        default=False,
        verbose_name="نمایش موقعیت دقیق در سایت",
        help_text=(
            "این گزینه فقط با اجازه مالک فعال شود. "
            "در حالت عادی از موقعیت تقریبی استفاده شود."
        ),
    )

    sale_price = models.DecimalField(
        max_digits=20,
        decimal_places=0,
        validators=[
            MinValueValidator(0),
        ],
        null=True,
        blank=True,
        verbose_name="قیمت فروش",
    )

    deposit_amount = models.DecimalField(
        max_digits=20,
        decimal_places=0,
        validators=[
            MinValueValidator(0),
        ],
        null=True,
        blank=True,
        verbose_name="مبلغ ودیعه یا رهن",
    )

    monthly_rent = models.DecimalField(
        max_digits=20,
        decimal_places=0,
        validators=[
            MinValueValidator(0),
        ],
        null=True,
        blank=True,
        verbose_name="اجاره ماهانه",
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
    )

    is_price_negotiable = models.BooleanField(
        default=False,
        verbose_name="قیمت قابل مذاکره است",
    )

    building_area = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name="متراژ بنا",
        help_text="برحسب مترمربع",
    )

    land_area = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name="متراژ زمین",
        help_text="برحسب مترمربع",
    )

    bedrooms = models.PositiveSmallIntegerField(
        default=0,
        verbose_name="تعداد اتاق خواب",
    )

    bathrooms = models.PositiveSmallIntegerField(
        default=0,
        verbose_name="تعداد حمام و سرویس",
    )

    parking_spaces = models.PositiveSmallIntegerField(
        default=0,
        verbose_name="تعداد پارکینگ",
    )

    year_built = models.PositiveSmallIntegerField(
        null=True,
        blank=True,
        verbose_name="سال ساخت",
        help_text=(
            "سال شمسی یا میلادی به‌صورت چهاررقمی وارد شود."
        ),
    )

    floor_number = models.SmallIntegerField(
        null=True,
        blank=True,
        verbose_name="شماره طبقه",
    )

    total_floors = models.PositiveSmallIntegerField(
        null=True,
        blank=True,
        verbose_name="تعداد کل طبقات",
    )

    deed_type = models.CharField(
        max_length=30,
        choices=DeedType.choices,
        default=DeedType.UNKNOWN,
        verbose_name="نوع سند",
    )

    deed_description = models.CharField(
        max_length=250,
        blank=True,
        verbose_name="توضیح سند",
    )

    is_document_verified = models.BooleanField(
        default=False,
        verbose_name="مدارک توسط مجموعه بررسی شده است",
        help_text=(
            "این گزینه صرفاً نشان‌دهنده بررسی داخلی است "
            "و تضمین حقوقی اصالت سند محسوب نمی‌شود."
        ),
    )

    is_featured = models.BooleanField(
        default=False,
        verbose_name="ملک ویژه",
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

        verbose_name = "ملک"
        verbose_name_plural = "املاک"

        indexes = [
            models.Index(
                fields=[
                    "publication_status",
                    "availability_status",
                    "transaction_type",
                ],
                name="property_pub_avail_tx_idx",
            ),
            models.Index(
                fields=[
                    "region",
                    "property_type",
                ],
                name="property_region_type_idx",
            ),
            models.Index(
                fields=[
                    "project",
                    "publication_status",
                ],
                name="property_project_pub_idx",
            ),
            models.Index(
                fields=[
                    "is_featured",
                    "publication_status",
                ],
                name="property_featured_pub_idx",
            ),
        ]

        constraints = [
            models.CheckConstraint(
                condition=(
                    Q(sale_price__isnull=True)
                    | Q(sale_price__gte=0)
                ),
                name="prop_sale_price_gte_0",
            ),
            models.CheckConstraint(
                condition=(
                    Q(deposit_amount__isnull=True)
                    | Q(deposit_amount__gte=0)
                ),
                name="prop_deposit_gte_0",
            ),
            models.CheckConstraint(
                condition=(
                    Q(monthly_rent__isnull=True)
                    | Q(monthly_rent__gte=0)
                ),
                name="prop_monthly_rent_gte_0",
            ),
            models.CheckConstraint(
                condition=(
                    Q(floor_number__isnull=True)
                    | Q(total_floors__isnull=True)
                    | Q(floor_number__lte=F("total_floors"))
                ),
                name="prop_floor_lte_total",
            ),
        ]

    def __str__(self):
        return f"{self.reference_code} - {self.title}"

    def clean(self):
        """
        Validate business rules before saving the property.
        """
        super().clean()

        errors = {}

        if (
            self.project_id
            and self.region_id
            and self.project.region_id != self.region_id
        ):
            errors["project"] = (
                "منطقه ملک باید با منطقه پروژه انتخاب‌شده "
                "یکسان باشد."
            )

        if (
            self.floor_number is not None
            and self.total_floors is not None
            and self.floor_number > self.total_floors
        ):
            errors["floor_number"] = (
                "شماره طبقه نمی‌تواند از تعداد کل طبقات "
                "بیشتر باشد."
            )

        if (
            self.year_built is not None
            and not 1000 <= self.year_built <= 2100
        ):
            errors["year_built"] = (
                "سال ساخت باید یک سال چهاررقمی معتبر "
                "بین 1000 و 2100 باشد."
            )

        if (
            self.is_exact_location_public
            and (
                self.latitude is None
                or self.longitude is None
            )
        ):
            errors["is_exact_location_public"] = (
                "برای نمایش موقعیت دقیق، عرض و طول "
                "جغرافیایی باید ثبت شوند."
            )

        if (
            self.transaction_type
            == self.TransactionType.FULL_MORTGAGE
            and self.monthly_rent not in (
                None,
                0,
            )
        ):
            errors["monthly_rent"] = (
                "برای رهن کامل، اجاره ماهانه باید خالی "
                "یا صفر باشد."
            )

        is_published = (
            self.publication_status
            == self.PublicationStatus.PUBLISHED
        )

        if is_published and not self.price_on_request:
            if self.transaction_type in (
                self.TransactionType.SALE,
                self.TransactionType.PRE_SALE,
            ):
                if (
                    self.sale_price is None
                    or self.sale_price <= 0
                ):
                    errors["sale_price"] = (
                        "برای انتشار ملک فروشی یا پیش‌فروش، "
                        "قیمت فروش باید بیشتر از صفر باشد."
                    )

            elif (
                self.transaction_type
                == self.TransactionType.RENT
            ):
                if (
                    self.monthly_rent is None
                    or self.monthly_rent <= 0
                ):
                    errors["monthly_rent"] = (
                        "برای انتشار ملک اجاره‌ای، "
                        "اجاره ماهانه باید بیشتر از صفر باشد."
                    )

            elif (
                self.transaction_type
                == self.TransactionType.MORTGAGE_RENT
            ):
                if (
                    self.deposit_amount is None
                    or self.deposit_amount <= 0
                ):
                    errors["deposit_amount"] = (
                        "برای رهن و اجاره، مبلغ ودیعه "
                        "باید بیشتر از صفر باشد."
                    )

                if (
                    self.monthly_rent is None
                    or self.monthly_rent <= 0
                ):
                    errors["monthly_rent"] = (
                        "برای رهن و اجاره، اجاره ماهانه "
                        "باید بیشتر از صفر باشد."
                    )

            elif (
                self.transaction_type
                == self.TransactionType.FULL_MORTGAGE
            ):
                if (
                    self.deposit_amount is None
                    or self.deposit_amount <= 0
                ):
                    errors["deposit_amount"] = (
                        "برای رهن کامل، مبلغ رهن باید "
                        "بیشتر از صفر باشد."
                    )

        if errors:
            raise ValidationError(errors)

    def publish(self):
        """
        Publish the property after full validation.

        The property must already exist and have a cover image.
        """
        if self.pk is None:
            raise ValidationError(
                {
                    "publication_status": (
                        "ابتدا ملک را ذخیره و تصویر کاور "
                        "را ثبت کنید."
                    ),
                },
            )

        self.publication_status = (
            self.PublicationStatus.PUBLISHED
        )

        if self.published_at is None:
            self.published_at = timezone.now()

        self.full_clean()

        if not self.images.filter(
            is_cover=True,
        ).exists():
            raise ValidationError(
                {
                    "publication_status": (
                        "برای انتشار ملک باید یک تصویر "
                        "کاور انتخاب شود."
                    ),
                },
            )

        self.save(
            update_fields=[
                "publication_status",
                "published_at",
                "updated_at",
            ],
        )

    def move_to_draft(self):
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
        self.publication_status = (
            self.PublicationStatus.ARCHIVED
        )

        self.save(
            update_fields=[
                "publication_status",
                "updated_at",
            ],
        )

    def mark_as_reserved(self):
        self.availability_status = (
            self.AvailabilityStatus.RESERVED
        )

        self.save(
            update_fields=[
                "availability_status",
                "updated_at",
            ],
        )

    def mark_as_sold(self):
        self.availability_status = (
            self.AvailabilityStatus.SOLD
        )

        self.save(
            update_fields=[
                "availability_status",
                "updated_at",
            ],
        )

    def mark_as_rented(self):
        self.availability_status = (
            self.AvailabilityStatus.RENTED
        )

        self.save(
            update_fields=[
                "availability_status",
                "updated_at",
            ],
        )

    def mark_as_unavailable(self):
        self.availability_status = (
            self.AvailabilityStatus.UNAVAILABLE
        )

        self.save(
            update_fields=[
                "availability_status",
                "updated_at",
            ],
        )


class PropertyPrivateDetails(TimeStampedModel):
    property = models.OneToOneField(
        Property,
        on_delete=models.CASCADE,
        related_name="private_details",
        verbose_name="ملک",
    )

    exact_address = models.TextField(
        blank=True,
        verbose_name="آدرس دقیق",
    )

    owner_name = models.CharField(
        max_length=150,
        blank=True,
        verbose_name="نام مالک",
    )

    owner_phone = models.CharField(
        max_length=30,
        blank=True,
        validators=[
            phone_number_validator,
        ],
        verbose_name="شماره تماس مالک",
    )

    owner_notes = models.TextField(
        blank=True,
        verbose_name="یادداشت داخلی مالک",
    )

    exact_latitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        validators=[
            MinValueValidator(-90),
            MaxValueValidator(90),
        ],
        null=True,
        blank=True,
        verbose_name="عرض جغرافیایی دقیق",
    )

    exact_longitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        validators=[
            MinValueValidator(-180),
            MaxValueValidator(180),
        ],
        null=True,
        blank=True,
        verbose_name="طول جغرافیایی دقیق",
    )

    class Meta:
        verbose_name = "اطلاعات خصوصی ملک"
        verbose_name_plural = "اطلاعات خصوصی املاک"

    def __str__(self):
        return (
            f"اطلاعات خصوصی ملک "
            f"{self.property.reference_code}"
        )


class PropertyImage(TimeStampedModel):
    property = models.ForeignKey(
        Property,
        on_delete=models.CASCADE,
        related_name="images",
        verbose_name="ملک",
    )

    image = models.ImageField(
        upload_to="properties/images/",
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
                    "property",
                ],
                condition=Q(is_cover=True),
                name="unique_cover_image_per_property",
            ),
        ]

        verbose_name = "تصویر ملک"
        verbose_name_plural = "تصاویر ملک"

    def __str__(self):
        return f"تصویر ملک {self.property.reference_code}"