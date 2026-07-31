from django.db import models

from apps.core.models import TimeStampedModel


class Inquiry(TimeStampedModel):
    class Status(models.TextChoices):
        NEW = "new", "New"
        CONTACTED = "contacted", "Contacted"
        IN_PROGRESS = "in_progress", "In Progress"
        CLOSED = "closed", "Closed"
        SPAM = "spam", "Spam"

    class PreferredContactMethod(models.TextChoices):
        PHONE = "phone", "Phone"
        WHATSAPP = "whatsapp", "WhatsApp"
        EMAIL = "email", "Email"

    full_name = models.CharField(max_length=150)
    phone = models.CharField(max_length=30)
    email = models.EmailField(blank=True)

    preferred_contact_method = models.CharField(
        max_length=20,
        choices=PreferredContactMethod.choices,
        default=PreferredContactMethod.PHONE,
    )

    property = models.ForeignKey(
        "properties.Property",
        on_delete=models.SET_NULL,
        related_name="inquiries",
        null=True,
        blank=True,
    )
    project = models.ForeignKey(
        "projects.DevelopmentProject",
        on_delete=models.SET_NULL,
        related_name="inquiries",
        null=True,
        blank=True,
    )
    assigned_agent = models.ForeignKey(
        "agents.Agent",
        on_delete=models.SET_NULL,
        related_name="assigned_inquiries",
        null=True,
        blank=True,
    )

    message = models.TextField()
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.NEW,
    )
    admin_notes = models.TextField(blank=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Inquiry"
        verbose_name_plural = "Inquiries"
        constraints = [
            models.CheckConstraint(
                condition=~(
                    models.Q(property__isnull=False)
                    & models.Q(project__isnull=False)
                ),
                name="inquiry_cannot_target_property_and_project",
            ),
        ]
        indexes = [
            models.Index(fields=["status", "created_at"]),
            models.Index(fields=["phone"]),
        ]

    def __str__(self):
        return f"{self.full_name} - {self.phone}"