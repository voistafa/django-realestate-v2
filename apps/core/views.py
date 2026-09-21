from django.db.models import Prefetch
from django.shortcuts import render

from apps.agents.models import Agent
from apps.organization.models import OrganizationMember
from apps.projects.models import (
    DevelopmentProject,
    ProjectImage,
)
from apps.properties.models import (
    Property,
    PropertyImage,
)


def home(request):
    """
    Display featured and publicly available content.
    """

    featured_properties = (
        Property.objects.filter(
            publication_status=Property.PublicationStatus.PUBLISHED,
            availability_status__in=(
                Property.AvailabilityStatus.AVAILABLE,
                Property.AvailabilityStatus.RESERVED,
            ),
            is_featured=True,
        )
        .select_related(
            "property_type",
            "region",
            "region__city",
            "project",
            "agent",
        )
        .prefetch_related(
            Prefetch(
                "images",
                queryset=PropertyImage.objects.order_by(
                    "-is_cover",
                    "display_order",
                    "created_at",
                ),
                to_attr="home_images",
            ),
        )
        .order_by(
            "-published_at",
            "-created_at",
        )[:6]
    )

    featured_projects = (
        DevelopmentProject.objects.filter(
            publication_status=(
                DevelopmentProject.PublicationStatus.PUBLISHED
            ),
            is_featured=True,
        )
        .select_related(
            "region",
            "region__city",
            "agent",
        )
        .prefetch_related(
            Prefetch(
                "images",
                queryset=ProjectImage.objects.order_by(
                    "-is_cover",
                    "display_order",
                    "created_at",
                ),
                to_attr="home_images",
            ),
        )
        .order_by(
            "-published_at",
            "-created_at",
        )[:4]
    )

    featured_agents = (
        Agent.objects.filter(
            is_active=True,
            is_featured=True,
        )
        .prefetch_related(
            "service_regions",
        )
        .order_by(
            "display_order",
            "full_name",
        )[:5]
    )

    primary_manager = (
        OrganizationMember.objects.filter(
            is_primary_manager=True,
            is_active=True,
        )
        .first()
    )

    organization_members = (
        OrganizationMember.objects.filter(
            is_active=True,
            is_primary_manager=False,
        )
        .order_by(
            "display_order",
            "full_name",
        )[:5]
    )

    context = {
        "featured_properties": featured_properties,
        "featured_projects": featured_projects,
        "featured_agents": featured_agents,
        "primary_manager": primary_manager,
        "organization_members": organization_members,
    }

    return render(
        request,
        "core/home.html",
        context,
    )