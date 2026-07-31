from django.core.validators import MinValueValidator
from django.db import models
from django.utils import timezone

from apps.core.models import TimeStampedModel


class PropertyType(TimeStampedModel):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=120, unique=True)
    is_active = models.BooleanField(default=True)
    display_order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ["display_order", "name"]
        verbose_name = "Property Type"
        verbose_name_plural = "Property Types"

    def __str__(self):
        return self.name


class Feature(TimeStampedModel):
    name = models.CharField(max_length=120, unique=True)
    icon = models.CharField(max_length=80, blank=True)
    is_active = models.BooleanField(default=True)
    display_order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ["display_order", "name"]
        verbose_name = "Feature"
        verbose_name_plural = "Features"

    def __str__(self):
        return self.name


class Property(TimeStampedModel):
    class ListingType(models.TextChoices):
        SALE = "sale", "For Sale"
        RENT = "rent", "For Rent"

    class Status(models.TextChoices):
        DRAFT = "draft", "Draft"
        PUBLISHED = "published", "Published"
        SOLD = "sold", "Sold"
        RENTED = "rented", "Rented"
        ARCHIVED = "archived", "Archived"

    class Currency(models.TextChoices):
        IRR = "IRR", "Iranian Rial"
        USD = "USD", "US Dollar"
        EUR = "EUR", "Euro"
        AED = "AED", "UAE Dirham"

    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=220, unique=True)
    reference_code = models.CharField(max_length=30, unique=True)

    property_type = models.ForeignKey(
        PropertyType,
        on_delete=models.PROTECT,
        related_name="properties",
    )
    region = models.ForeignKey(
        "locations.Region",
        on_delete=models.PROTECT,
        related_name="properties",
    )
    agent = models.ForeignKey(
        "agents.Agent",
        on_delete=models.SET_NULL,
        related_name="properties",
        null=True,
        blank=True,
    )
    features = models.ManyToManyField(
        Feature,
        related_name="properties",
        blank=True,
    )

    listing_type = models.CharField(
        max_length=10,
        choices=ListingType.choices,
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.DRAFT,
    )

    short_description = models.CharField(max_length=300, blank=True)
    description = models.TextField()
    address = models.CharField(max_length=300, blank=True)

    price = models.DecimalField(
        max_digits=20,
        decimal_places=0,
        validators=[MinValueValidator(0)],
    )
    currency_code = models.CharField(
        max_length=3,
        choices=Currency.choices,
        default=Currency.IRR,
    )

    building_area = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="Building area in square metres",
    )
    land_area = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="Land area in square metres",
    )
    bedrooms = models.PositiveSmallIntegerField(default=0)
    bathrooms = models.PositiveSmallIntegerField(default=0)
    parking_spaces = models.PositiveSmallIntegerField(default=0)

    year_built = models.PositiveSmallIntegerField(
        null=True,
        blank=True,
    )
    floor_number = models.SmallIntegerField(
        null=True,
        blank=True,
    )
    total_floors = models.PositiveSmallIntegerField(
        null=True,
        blank=True,
    )

    latitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        null=True,
        blank=True,
    )
    longitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        null=True,
        blank=True,
    )

    is_featured = models.BooleanField(default=False)
    published_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-published_at", "-created_at"]
        verbose_name = "Property"
        verbose_name_plural = "Properties"
        indexes = [
            models.Index(fields=["status", "listing_type"]),
            models.Index(fields=["region", "property_type"]),
            models.Index(fields=["is_featured", "status"]),
        ]

    def __str__(self):
        return f"{self.reference_code} - {self.title}"

    def publish(self):
        self.status = self.Status.PUBLISHED

        if self.published_at is None:
            self.published_at = timezone.now()

        self.save(update_fields=["status", "published_at", "updated_at"])