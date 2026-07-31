from django.core.validators import MinValueValidator
from django.db import models

from apps.core.models import TimeStampedModel


class Agent(TimeStampedModel):
    full_name = models.CharField(max_length=150)
    slug = models.SlugField(max_length=170, unique=True)
    job_title = models.CharField(max_length=120, blank=True)

    photo = models.ImageField(
        upload_to="agents/photos/",
        blank=True,
    )

    phone = models.CharField(max_length=30, blank=True)
    whatsapp = models.CharField(max_length=30, blank=True)
    email = models.EmailField(blank=True)

    bio = models.TextField(blank=True)

    experience_years = models.PositiveSmallIntegerField(
        default=0,
        validators=[MinValueValidator(0)],
    )

    instagram_url = models.URLField(blank=True)
    linkedin_url = models.URLField(blank=True)

    is_featured = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    display_order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ["display_order", "full_name"]
        verbose_name = "Agent"
        verbose_name_plural = "Agents"

    def __str__(self):
        return self.full_name