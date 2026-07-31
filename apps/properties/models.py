from django.db import models

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