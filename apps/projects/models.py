from django.db import models

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