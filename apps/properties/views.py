from decimal import Decimal, InvalidOperation

from django.core.paginator import Paginator
from django.db.models import (
    Case,
    DecimalField,
    F,
    Prefetch,
    Q,
    When,
)
from django.shortcuts import (
    get_object_or_404,
    render,
)

from apps.locations.models import Region

from .models import (
    Feature,
    Property,
    PropertyImage,
    PropertyType,
)

from apps.agents.models import Agent


PUBLIC_AVAILABILITY_STATUSES = (
    Property.AvailabilityStatus.AVAILABLE,
    Property.AvailabilityStatus.RESERVED,
)


def parse_positive_decimal(value):
    """
    Convert a query-string value to a non-negative Decimal.

    Empty, invalid, or negative values return None.
    Thousand separators and spaces are removed before parsing.
    """
    if not value:
        return None

    try:
        normalized_value = (
            str(value)
            .replace(",", "")
            .replace("٬", "")
            .replace(" ", "")
            .replace("\u00a0", "")
            .strip()
        )

        if not normalized_value:
            return None

        number = Decimal(normalized_value)

    except (
        InvalidOperation,
        TypeError,
        ValueError,
    ):
        return None

    if number < 0:
        return None

    return number


def effective_price_expression():
    """
    Return the primary price used for filtering and ordering.

    Sale and pre-sale:
        sale_price

    Full mortgage:
        deposit_amount

    Rent and mortgage-rent:
        monthly_rent
    """
    return Case(
        When(
            transaction_type__in=(
                Property.TransactionType.SALE,
                Property.TransactionType.PRE_SALE,
            ),
            then=F("sale_price"),
        ),
        When(
            transaction_type=(
                Property.TransactionType.FULL_MORTGAGE
            ),
            then=F("deposit_amount"),
        ),
        When(
            transaction_type__in=(
                Property.TransactionType.RENT,
                Property.TransactionType.MORTGAGE_RENT,
            ),
            then=F("monthly_rent"),
        ),
        default=None,
        output_field=DecimalField(
            max_digits=20,
            decimal_places=0,
        ),
    )


def property_list(request):
    """
    Display publicly published and available properties.

    Supported capabilities:
    - Text search
    - Transaction type filtering
    - Property type filtering
    - Region filtering
    - Bedroom filtering
    - Price filtering
    - Deposit filtering
    - Ordering
    - Pagination
    """
    properties_queryset = (
        Property.objects.filter(
            publication_status=(
                Property.PublicationStatus.PUBLISHED
            ),
            availability_status__in=(
                PUBLIC_AVAILABILITY_STATUSES
            ),
        )
        .annotate(
            effective_price=effective_price_expression(),
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
                to_attr="list_images",
            ),
        )
    )

    search_query = request.GET.get(
        "q",
        "",
    ).strip()

    transaction_type = request.GET.get(
        "transaction_type",
        "",
    ).strip()

    property_type_id = request.GET.get(
        "property_type",
        "",
    ).strip()

    region_id = request.GET.get(
        "region",
        "",
    ).strip()

    bedrooms = request.GET.get(
        "bedrooms",
        "",
    ).strip()

    minimum_price_value = request.GET.get(
        "min_price",
        "",
    ).strip()

    maximum_price_value = request.GET.get(
        "max_price",
        "",
    ).strip()

    minimum_deposit_value = request.GET.get(
        "min_deposit",
        "",
    ).strip()

    maximum_deposit_value = request.GET.get(
        "max_deposit",
        "",
    ).strip()

    ordering = request.GET.get(
        "ordering",
        "newest",
    ).strip()

    if search_query:
        properties_queryset = properties_queryset.filter(
            Q(title__icontains=search_query)
            | Q(reference_code__icontains=search_query)
            | Q(short_description__icontains=search_query)
            | Q(description__icontains=search_query)
            | Q(public_location__icontains=search_query)
            | Q(region__name__icontains=search_query)
            | Q(region__city__name__icontains=search_query)
            | Q(property_type__name__icontains=search_query)
            | Q(project__title__icontains=search_query)
        )

    valid_transaction_types = {
        value
        for value, _ in Property.TransactionType.choices
    }

    if transaction_type in valid_transaction_types:
        properties_queryset = properties_queryset.filter(
            transaction_type=transaction_type,
        )
    else:
        transaction_type = ""

    if property_type_id.isdigit():
        properties_queryset = properties_queryset.filter(
            property_type_id=int(property_type_id),
        )
    else:
        property_type_id = ""

    if region_id.isdigit():
        properties_queryset = properties_queryset.filter(
            region_id=int(region_id),
        )
    else:
        region_id = ""

    if bedrooms in {
        "1",
        "2",
        "3",
    }:
        properties_queryset = properties_queryset.filter(
            bedrooms=int(bedrooms),
        )

    elif bedrooms == "4":
        properties_queryset = properties_queryset.filter(
            bedrooms__gte=4,
        )

    else:
        bedrooms = ""

    minimum_price = parse_positive_decimal(
        minimum_price_value,
    )

    maximum_price = parse_positive_decimal(
        maximum_price_value,
    )

    minimum_deposit = parse_positive_decimal(
        minimum_deposit_value,
    )

    maximum_deposit = parse_positive_decimal(
        maximum_deposit_value,
    )

    if minimum_price is not None:
        properties_queryset = properties_queryset.filter(
            effective_price__gte=minimum_price,
        )

    if maximum_price is not None:
        properties_queryset = properties_queryset.filter(
            effective_price__lte=maximum_price,
        )

    if minimum_deposit is not None:
        properties_queryset = properties_queryset.filter(
            deposit_amount__gte=minimum_deposit,
        )

    if maximum_deposit is not None:
        properties_queryset = properties_queryset.filter(
            deposit_amount__lte=maximum_deposit,
        )

    ordering_options = {
        "newest": (
            "-published_at",
            "-created_at",
        ),
        "oldest": (
            "published_at",
            "created_at",
        ),
        "price_asc": (
            F("effective_price").asc(
                nulls_last=True,
            ),
            "-published_at",
        ),
        "price_desc": (
            F("effective_price").desc(
                nulls_last=True,
            ),
            "-published_at",
        ),
        "area_desc": (
            F("land_area").desc(
                nulls_last=True,
            ),
            F("building_area").desc(
                nulls_last=True,
            ),
            "-published_at",
        ),
    }

    selected_ordering_key = (
        ordering
        if ordering in ordering_options
        else "newest"
    )

    properties_queryset = properties_queryset.order_by(
        *ordering_options[selected_ordering_key],
    )

    paginator = Paginator(
        properties_queryset,
        9,
    )

    page_obj = paginator.get_page(
        request.GET.get("page"),
    )

    query_parameters = request.GET.copy()

    query_parameters.pop(
        "page",
        None,
    )

    query_string = query_parameters.urlencode()

    context = {
    "page_obj": page_obj,
    "properties": page_obj.object_list,
    "primary_manager": {
        "phone": "+989309932199",
    },
    "property_types": PropertyType.objects.filter(
        is_active=True,
    ).order_by(
        "display_order",
        "name",
    ),
        "regions": Region.objects.select_related(
            "city",
        ).order_by(
            "city__name",
            "name",
        ),
        "transaction_types": (
            Property.TransactionType.choices
        ),
        "query_string": query_string,
        "selected_filters": {
            "q": search_query,
            "transaction_type": transaction_type,
            "property_type": property_type_id,
            "region": region_id,
            "bedrooms": bedrooms,
            "min_price": minimum_price_value,
            "max_price": maximum_price_value,
            "min_deposit": minimum_deposit_value,
            "max_deposit": maximum_deposit_value,
            "ordering": selected_ordering_key,
        },
    }

    return render(
        request,
        "properties/property_list.html",
        context,
    )


def property_detail(request, slug):
    """
    Display one publicly published property.

    Sold, rented, and temporarily unavailable properties can still
    retain their public detail page while their status is displayed.

    Private owner information and exact private address are not
    selected or passed to the public template.
    """
    property_queryset = (
        Property.objects.filter(
            publication_status=(
                Property.PublicationStatus.PUBLISHED
            ),
        )
        .annotate(
            effective_price=effective_price_expression(),
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
                to_attr="detail_images",
            ),
            Prefetch(
                "features",
                queryset=Feature.objects.filter(
                    is_active=True,
                ).order_by(
                    "display_order",
                    "name",
                ),
                to_attr="active_features",
            ),
        )
    )

    property_object = get_object_or_404(
        property_queryset,
        slug=slug,
    )

    similar_properties = (
        Property.objects.filter(
            publication_status=(
                Property.PublicationStatus.PUBLISHED
            ),
            availability_status__in=(
                PUBLIC_AVAILABILITY_STATUSES
            ),
        )
        .filter(
            Q(
                property_type=(
                    property_object.property_type
                ),
            )
            | Q(
                region=property_object.region,
            ),
        )
        .exclude(
            pk=property_object.pk,
        )
        .annotate(
            effective_price=effective_price_expression(),
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
                to_attr="list_images",
            ),
        )
        .order_by(
            "-is_featured",
            "-published_at",
            "-created_at",
        )[:3]
    )

    context = {
        "property": property_object,
        "property_images": property_object.detail_images,
        "property_features": property_object.active_features,
        "similar_properties": similar_properties,
    }

    return render(
        request,
        "properties/property_detail.html",
        context,
    )