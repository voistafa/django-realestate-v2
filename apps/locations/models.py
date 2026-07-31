from django.db import models

from apps.core.models import TimeStampedModel


class City(TimeStampedModel):
    name = models.CharField(max_length=120, unique=True)
    slug = models.SlugField(max_length=140, unique=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["name"]
        verbose_name = "City"
        verbose_name_plural = "Cities"

    def __str__(self):
        return self.name


class Region(TimeStampedModel):
    city = models.ForeignKey(
        City,
        on_delete=models.PROTECT,
        related_name="regions",
    )
    name = models.CharField(max_length=120)
    slug = models.SlugField(max_length=140)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["city__name", "name"]
        constraints = [
            models.UniqueConstraint(
                fields=["city", "name"],
                name="unique_region_name_per_city",
            ),
            models.UniqueConstraint(
                fields=["city", "slug"],
                name="unique_region_slug_per_city",
            ),
        ]
        verbose_name = "Region"
        verbose_name_plural = "Regions"

    def __str__(self):
        return f"{self.name}, {self.city.name}"