from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils import timezone

from apps.core.models import TimeStampedModel


class ProjectFeature(TimeStampedModel):
    name = models.CharField(max_length=120, unique=True)
    icon = models.CharField(max_length=80, blank=True)
    is_active = models.BooleanField(default=True)
    display_order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ["display_order", "name"]
        verbose_name = "Project Feature"
        verbose_name_plural = "Project Features"

    def __str__(self):
        return self.name


class DevelopmentProject(TimeStampedModel):
    class Status(models.TextChoices):
        PLANNING = "planning", "Planning"
        UNDER_CONSTRUCTION = "under_construction", "Under Construction"
        COMPLETED = "completed", "Completed"
        ON_HOLD = "on_hold", "On Hold"
        ARCHIVED = "archived", "Archived"

    class Currency(models.TextChoices):
        IRR = "IRR", "Iranian Rial"
        USD = "USD", "US Dollar"
        EUR = "EUR", "Euro"
        AED = "AED", "UAE Dirham"

    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=220, unique=True)
    reference_code = models.CharField(max_length=30, unique=True)

    region = models.ForeignKey(
        "locations.Region",
        on_delete=models.PROTECT,
        related_name="development_projects",
    )
    agent = models.ForeignKey(
        "agents.Agent",
        on_delete=models.SET_NULL,
        related_name="development_projects",
        null=True,
        blank=True,
    )
    features = models.ManyToManyField(
        ProjectFeature,
        related_name="development_projects",
        blank=True,
    )

    status = models.CharField(
        max_length=30,
        choices=Status.choices,
        default=Status.PLANNING,
    )

    short_description = models.CharField(max_length=300, blank=True)
    description = models.TextField()
    address = models.CharField(max_length=300, blank=True)
    developer_name = models.CharField(max_length=150, blank=True)

    starting_price = models.DecimalField(
        max_digits=20,
        decimal_places=0,
        validators=[MinValueValidator(0)],
        null=True,
        blank=True,
    )
    currency_code = models.CharField(
        max_length=3,
        choices=Currency.choices,
        default=Currency.IRR,
    )

    total_units = models.PositiveIntegerField(
        null=True,
        blank=True,
    )
    available_units = models.PositiveIntegerField(
        null=True,
        blank=True,
    )

    completion_percentage = models.PositiveSmallIntegerField(
        default=0,
        validators=[
            MinValueValidator(0),
            MaxValueValidator(100),
        ],
    )

    start_date = models.DateField(null=True, blank=True)
    expected_completion_date = models.DateField(null=True, blank=True)

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
        verbose_name = "Development Project"
        verbose_name_plural = "Development Projects"
        indexes = [
            models.Index(fields=["status", "region"]),
            models.Index(fields=["is_featured", "status"]),
        ]

    def __str__(self):
        return f"{self.reference_code} - {self.title}"

    def publish(self):
        if self.published_at is None:
            self.published_at = timezone.now()

        self.save(update_fields=["published_at", "updated_at"])

class ProjectImage(TimeStampedModel):
    project = models.ForeignKey(
        DevelopmentProject,
        on_delete=models.CASCADE,
        related_name="images",
    )
    image = models.ImageField(
        upload_to="projects/images/",
    )
    alt_text = models.CharField(max_length=200, blank=True)
    is_cover = models.BooleanField(default=False)
    display_order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ["display_order", "created_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["project"],
                condition=models.Q(is_cover=True),
                name="unique_cover_image_per_project",
            ),
        ]
        verbose_name = "Project Image"
        verbose_name_plural = "Project Images"

    def __str__(self):
        return f"Image for {self.project.reference_code}"