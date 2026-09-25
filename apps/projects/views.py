from django.core.paginator import Paginator
from django.db.models import Prefetch
from django.shortcuts import get_object_or_404, render

from .models import (
    DevelopmentProject,
    ProjectFeature,
    ProjectImage,
)


def project_list(request):
    """
    Display publicly published development projects.
    """
    projects_queryset = (
        DevelopmentProject.objects.filter(
            publication_status=DevelopmentProject.PublicationStatus.PUBLISHED,
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
                to_attr="list_images",
            ),
        )
        .order_by(
            "-published_at",
            "-created_at",
        )
    )

    paginator = Paginator(
        projects_queryset,
        9,
    )

    page_obj = paginator.get_page(
        request.GET.get("page"),
    )

    context = {
        "page_obj": page_obj,
        "projects": page_obj.object_list,
        "primary_manager": {
            "phone": "+989309932199",
        },
    }

    return render(
        request,
        "projects/project_list.html",
        context,
    )


def project_detail(request, slug):
    """
    Display one publicly published development project.
    """
    project_queryset = (
        DevelopmentProject.objects.filter(
            publication_status=DevelopmentProject.PublicationStatus.PUBLISHED,
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
                to_attr="detail_images",
            ),
            Prefetch(
                "features",
                queryset=ProjectFeature.objects.filter(
                    is_active=True,
                ).order_by(
                    "display_order",
                    "name",
                ),
                to_attr="active_features",
            ),
        )
        .defer(
            "private_address",
        )
    )

    project = get_object_or_404(
        project_queryset,
        slug=slug,
    )

    context = {
        "project": project,
        "project_images": project.detail_images,
        "project_features": project.active_features,
    }

    return render(
        request,
        "projects/project_detail.html",
        context,
    )