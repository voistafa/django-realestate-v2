from django.db import models

from apps.core.models import TimeStampedModel


class City(TimeStampedModel):
    name = models.CharField(
        max_length=120,
        unique=True,
        verbose_name="نام شهر",
    )

    slug = models.SlugField(
        max_length=140,
        unique=True,
        verbose_name="نامک",
        help_text=(
            "برای آدرس صفحه، از حروف انگلیسی، عدد "
            "و خط تیره استفاده شود."
        ),
    )

    is_active = models.BooleanField(
        default=True,
        verbose_name="فعال",
    )

    class Meta:
        ordering = [
            "name",
        ]
        verbose_name = "شهر"
        verbose_name_plural = "شهرها"

    def __str__(self):
        return self.name


class Region(TimeStampedModel):
    city = models.ForeignKey(
        City,
        on_delete=models.PROTECT,
        related_name="regions",
        verbose_name="شهر",
    )

    name = models.CharField(
        max_length=120,
        verbose_name="نام منطقه",
    )

    slug = models.SlugField(
        max_length=140,
        verbose_name="نامک",
        help_text=(
            "برای آدرس صفحه، از حروف انگلیسی، عدد "
            "و خط تیره استفاده شود."
        ),
    )

    is_active = models.BooleanField(
        default=True,
        verbose_name="فعال",
    )

    class Meta:
        ordering = [
            "city__name",
            "name",
        ]

        constraints = [
            models.UniqueConstraint(
                fields=[
                    "city",
                    "name",
                ],
                name="unique_region_name_per_city",
            ),
            models.UniqueConstraint(
                fields=[
                    "city",
                    "slug",
                ],
                name="unique_region_slug_per_city",
            ),
        ]

        verbose_name = "منطقه"
        verbose_name_plural = "مناطق"

    def __str__(self):
        return f"{self.city.name}، {self.name}"