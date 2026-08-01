from django.db.models import Prefetch
from django.shortcuts import render

from apps.agents.models import Agent
from apps.projects.models import DevelopmentProject, ProjectImage
from apps.properties.models import Property, PropertyImage


def home(request):
    featured_properties = (
        Property.objects.filter(
            status=Property.Status.PUBLISHED,
            is_featured=True,
        )
        .select_related(
            "property_type",
            "region",
            "region__city",
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
            )
        )
        [:6]
    )

    featured_projects = (
        DevelopmentProject.objects.filter(
            is_featured=True,
            published_at__isnull=False,
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
            )
        )
        [:4]
    )

    featured_agents = Agent.objects.filter(
        is_active=True,
        is_featured=True,
    )[:4]

    context = {
        "featured_properties": featured_properties,
        "featured_projects": featured_projects,
        "featured_agents": featured_agents,
    }

    return render(request, "core/home.html", context)