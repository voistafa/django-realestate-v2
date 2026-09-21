from django import forms
from django.contrib import admin, messages
from django.core.exceptions import ValidationError
from django.db.models import Prefetch, Q
from django.forms.models import BaseInlineFormSet
from django.utils import timezone
from django.utils.html import format_html

from apps.agents.models import Agent

from .models import (
    Feature,
    Property,
    PropertyImage,
    PropertyPrivateDetails,
    PropertyType,
)


@admin.register(PropertyType)
class PropertyTypeAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "slug",
        "is_active",
        "display_order",
    )

    list_editable = (
        "is_active",
        "display_order",
    )

    list_filter = (
        "is_active",
    )

    search_fields = (
        "name",
        "slug",
    )

    ordering = (
        "display_order",
        "name",
    )

    list_per_page = 30


@admin.register(Feature)
class FeatureAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "icon",
        "is_active",
        "display_order",
    )

    list_editable = (
        "is_active",
        "display_order",
    )

    list_filter = (
        "is_active",
    )

    search_fields = (
        "name",
        "icon",
    )

    ordering = (
        "display_order",
        "name",
    )

    list_per_page = 30


class PropertyImageAdminForm(forms.ModelForm):
    class Meta:
        model = PropertyImage
        fields = "__all__"

    def clean(self):
        cleaned_data = super().clean()

        property_object = cleaned_data.get("property")
        is_cover = cleaned_data.get("is_cover")

        if (
            property_object is not None
            and is_cover
            and PropertyImage.objects.filter(
                property=property_object,
                is_cover=True,
            )
            .exclude(pk=self.instance.pk)
            .exists()
        ):
            self.add_error(
                "is_cover",
                (
                    "این ملک از قبل تصویر کاور دارد. "
                    "ابتدا کاور قبلی را غیرفعال کنید."
                ),
            )

        return cleaned_data


class PropertyImageInlineFormSet(BaseInlineFormSet):
    def clean(self):
        super().clean()

        if any(self.errors):
            return

        cover_count = 0

        for form in self.forms:
            cleaned_data = getattr(
                form,
                "cleaned_data",
                None,
            )

            if not cleaned_data:
                continue

            if cleaned_data.get("DELETE"):
                continue

            if not cleaned_data.get("image"):
                continue

            if cleaned_data.get("is_cover"):
                cover_count += 1

        if cover_count > 1:
            raise ValidationError(
                (
                    "برای هر ملک فقط یک تصویر می‌تواند "
                    "به‌عنوان کاور انتخاب شود."
                ),
            )


class PropertyImageInline(admin.TabularInline):
    model = PropertyImage
    formset = PropertyImageInlineFormSet
    extra = 1

    fields = (
        "image",
        "alt_text",
        "is_cover",
        "display_order",
    )

    ordering = (
        "-is_cover",
        "display_order",
        "created_at",
    )


class PropertyPrivateDetailsInline(admin.StackedInline):
    model = PropertyPrivateDetails
    extra = 1
    max_num = 1
    min_num = 0
    validate_max = True
    can_delete = True

    fields = (
        "exact_address",
        (
            "owner_name",
            "owner_phone",
        ),
        "owner_notes",
        (
            "exact_latitude",
            "exact_longitude",
        ),
    )

    classes = (
        "collapse",
    )


@admin.register(Property)
class PropertyAdmin(admin.ModelAdmin):
    list_display = (
        "cover_thumbnail",
        "reference_code",
        "title",
        "property_type",
        "region",
        "transaction_type",
        "publication_status",
        "availability_status",
        "display_primary_price",
        "is_featured",
        "published_at",
    )

    list_filter = (
        "publication_status",
        "availability_status",
        "transaction_type",
        "property_type",
        "region__city",
        "region",
        "project",
        "agent",
        "is_featured",
        "price_on_request",
        "currency_code",
        "deed_type",
        "is_document_verified",
    )

    search_fields = (
        "reference_code",
        "title",
        "slug",
        "short_description",
        "description",
        "public_location",
        "region__name",
        "region__city__name",
        "project__title",
        "project__reference_code",
        "agent__full_name",
        "private_details__owner_name",
        "private_details__owner_phone",
        "private_details__exact_address",
    )

    autocomplete_fields = (
        "property_type",
        "region",
        "project",
    )

    filter_horizontal = (
        "features",
    )

    list_select_related = (
        "property_type",
        "region",
        "region__city",
        "project",
        "agent",
    )

    readonly_fields = (
        "published_at",
        "created_at",
        "updated_at",
    )

    fieldsets = (
        (
            "اطلاعات اصلی",
            {
                "fields": (
                    "reference_code",
                    "title",
                    "slug",
                ),
            },
        ),
        (
            "دسته‌بندی و مسئول",
            {
                "fields": (
                    (
                        "property_type",
                        "region",
                    ),
                    (
                        "project",
                        "agent",
                    ),
                    "features",
                ),
            },
        ),
        (
            "نوع معامله و وضعیت‌ها",
            {
                "fields": (
                    (
                        "transaction_type",
                        "publication_status",
                    ),
                    (
                        "availability_status",
                        "is_featured",
                    ),
                    "published_at",
                ),
            },
        ),
        (
            "توضیحات عمومی",
            {
                "fields": (
                    "short_description",
                    "description",
                    "public_location",
                ),
            },
        ),
        (
            "قیمت",
            {
                "fields": (
                    (
                        "sale_price",
                        "deposit_amount",
                    ),
                    (
                        "monthly_rent",
                        "currency_code",
                    ),
                    (
                        "price_on_request",
                        "is_price_negotiable",
                    ),
                ),
                "description": (
                    "فقط مبالغ مرتبط با نوع معامله را وارد کنید. "
                    "برای قیمت توافقی، گزینه «تماس بگیرید» را فعال کنید."
                ),
            },
        ),
        (
            "متراژ و مشخصات فنی",
            {
                "fields": (
                    (
                        "land_area",
                        "building_area",
                    ),
                    (
                        "bedrooms",
                        "bathrooms",
                        "parking_spaces",
                    ),
                    (
                        "year_built",
                        "floor_number",
                        "total_floors",
                    ),
                ),
            },
        ),
        (
            "اطلاعات سند",
            {
                "fields": (
                    "deed_type",
                    "deed_description",
                    "is_document_verified",
                ),
            },
        ),
        (
            "موقعیت عمومی روی نقشه",
            {
                "fields": (
                    (
                        "latitude",
                        "longitude",
                    ),
                    "is_exact_location_public",
                ),
                "classes": (
                    "collapse",
                ),
            },
        ),
        (
            "اطلاعات سیستمی",
            {
                "fields": (
                    "created_at",
                    "updated_at",
                ),
                "classes": (
                    "collapse",
                ),
            },
        ),
    )

    date_hierarchy = "published_at"

    ordering = (
        "-published_at",
        "-created_at",
    )

    actions = (
        "publish_selected_properties",
        "move_selected_properties_to_draft",
        "archive_selected_properties",
        "mark_selected_as_available",
        "mark_selected_as_reserved",
        "mark_selected_as_sold",
        "mark_selected_as_rented",
        "mark_selected_as_unavailable",
    )

    inlines = (
        PropertyPrivateDetailsInline,
        PropertyImageInline,
    )

    list_per_page = 25
    save_on_top = True

    class Media:
        css = {
            "all": (
                "properties/admin/property_form.css",
            ),
        }

    def get_queryset(self, request):
        queryset = super().get_queryset(request)

        return queryset.select_related(
            "property_type",
            "region",
            "region__city",
            "project",
            "agent",
        ).prefetch_related(
            Prefetch(
                "images",
                queryset=PropertyImage.objects.filter(
                    is_cover=True,
                ),
                to_attr="admin_cover_images",
            ),
        )

    def formfield_for_foreignkey(
        self,
        db_field,
        request,
        **kwargs,
    ):
        if db_field.name == "agent":
            current_agent_id = None

            if request.resolver_match:
                object_id = (
                    request.resolver_match.kwargs.get(
                        "object_id",
                    )
                )

                if object_id:
                    current_agent_id = (
                        Property.objects.filter(
                            pk=object_id,
                        )
                        .values_list(
                            "agent_id",
                            flat=True,
                        )
                        .first()
                    )

            kwargs["queryset"] = (
                Agent.objects.filter(
                    Q(is_active=True)
                    | Q(pk=current_agent_id),
                )
                .distinct()
                .order_by(
                    "display_order",
                    "full_name",
                )
            )

        return super().formfield_for_foreignkey(
            db_field,
            request,
            **kwargs,
        )

    @admin.display(
        description="کاور",
    )
    def cover_thumbnail(self, obj):
        images = getattr(
            obj,
            "admin_cover_images",
            [],
        )

        if not images:
            return "—"

        image = images[0]

        if not image.image:
            return "—"

        return format_html(
            (
                '<img src="{}" alt="" '
                'style="width:90px;height:65px;'
                'object-fit:cover;border-radius:8px;">'
            ),
            image.image.url,
        )

    @admin.display(
        description="قیمت",
    )
    def display_primary_price(self, obj):
        if obj.price_on_request:
            return "تماس بگیرید"

        currency_label = obj.get_currency_code_display()
        price_parts = []

        if obj.transaction_type in (
            Property.TransactionType.SALE,
            Property.TransactionType.PRE_SALE,
        ):
            if obj.sale_price is not None:
                price_parts.append(
                    f"{obj.sale_price:,.0f} {currency_label}"
                )

        elif (
            obj.transaction_type
            == Property.TransactionType.FULL_MORTGAGE
        ):
            if obj.deposit_amount is not None:
                price_parts.append(
                    (
                        f"رهن کامل: "
                        f"{obj.deposit_amount:,.0f} "
                        f"{currency_label}"
                    ),
                )

        else:
            if obj.deposit_amount is not None:
                price_parts.append(
                    (
                        f"رهن: "
                        f"{obj.deposit_amount:,.0f} "
                        f"{currency_label}"
                    ),
                )

            if obj.monthly_rent is not None:
                price_parts.append(
                    (
                        f"اجاره: "
                        f"{obj.monthly_rent:,.0f} "
                        f"{currency_label}"
                    ),
                )

        if not price_parts:
            return "—"

        if obj.is_price_negotiable:
            price_parts.append("قابل مذاکره")

        return " | ".join(price_parts)

    def save_model(
        self,
        request,
        obj,
        form,
        change,
    ):
        if (
            obj.publication_status
            == Property.PublicationStatus.PUBLISHED
            and obj.published_at is None
        ):
            obj.published_at = timezone.now()

        elif obj.publication_status in (
            Property.PublicationStatus.DRAFT,
            Property.PublicationStatus.PENDING_REVIEW,
        ):
            obj.published_at = None

        super().save_model(
            request,
            obj,
            form,
            change,
        )

    def save_related(
        self,
        request,
        form,
        formsets,
        change,
    ):
        super().save_related(
            request,
            form,
            formsets,
            change,
        )

        obj = form.instance

        if (
            obj.publication_status
            == Property.PublicationStatus.PUBLISHED
            and not obj.images.filter(
                is_cover=True,
            ).exists()
        ):
            obj.move_to_draft()

            self.message_user(
                request,
                (
                    "ملک ذخیره شد، اما به‌دلیل نداشتن تصویر "
                    "کاور به حالت پیش‌نویس بازگردانده شد."
                ),
                level=messages.WARNING,
            )

        elif (
            obj.publication_status
            == Property.PublicationStatus.PUBLISHED
            and obj.agent_id is None
        ):
            self.message_user(
                request,
                (
                    "ملک منتشر شد، اما مشاور مسئول ندارد. "
                    "در صفحه عمومی باید اطلاعات تماس مجموعه نمایش داده شود."
                ),
                level=messages.WARNING,
            )

    @admin.action(
        description="انتشار املاک انتخاب‌شده",
    )
    def publish_selected_properties(
        self,
        request,
        queryset,
    ):
        published_count = 0
        failed_codes = []

        for property_object in queryset:
            try:
                property_object.publish()
                published_count += 1
            except ValidationError:
                failed_codes.append(
                    property_object.reference_code,
                )

        if published_count:
            self.message_user(
                request,
                (
                    f"{published_count} ملک "
                    "با موفقیت منتشر شد."
                ),
                level=messages.SUCCESS,
            )

        if failed_codes:
            self.message_user(
                request,
                (
                    "برخی املاک به‌دلیل اطلاعات ناقص یا "
                    "نداشتن تصویر کاور منتشر نشدند: "
                    + "، ".join(failed_codes[:10])
                ),
                level=messages.WARNING,
            )

    @admin.action(
        description="انتقال املاک انتخاب‌شده به پیش‌نویس",
    )
    def move_selected_properties_to_draft(
        self,
        request,
        queryset,
    ):
        updated_count = queryset.update(
            publication_status=(
                Property.PublicationStatus.DRAFT
            ),
            published_at=None,
            updated_at=timezone.now(),
        )

        self.message_user(
            request,
            (
                f"{updated_count} ملک "
                "به پیش‌نویس منتقل شد."
            ),
            level=messages.SUCCESS,
        )

    @admin.action(
        description="بایگانی املاک انتخاب‌شده",
    )
    def archive_selected_properties(
        self,
        request,
        queryset,
    ):
        updated_count = queryset.update(
            publication_status=(
                Property.PublicationStatus.ARCHIVED
            ),
            updated_at=timezone.now(),
        )

        self.message_user(
            request,
            f"{updated_count} ملک بایگانی شد.",
            level=messages.SUCCESS,
        )

    @admin.action(
        description="علامت‌گذاری به‌عنوان موجود",
    )
    def mark_selected_as_available(
        self,
        request,
        queryset,
    ):
        updated_count = queryset.update(
            availability_status=(
                Property.AvailabilityStatus.AVAILABLE
            ),
            updated_at=timezone.now(),
        )

        self.message_user(
            request,
            f"{updated_count} ملک موجود شد.",
            level=messages.SUCCESS,
        )

    @admin.action(
        description="علامت‌گذاری به‌عنوان رزروشده",
    )
    def mark_selected_as_reserved(
        self,
        request,
        queryset,
    ):
        updated_count = queryset.update(
            availability_status=(
                Property.AvailabilityStatus.RESERVED
            ),
            updated_at=timezone.now(),
        )

        self.message_user(
            request,
            f"{updated_count} ملک رزرو شد.",
            level=messages.SUCCESS,
        )

    @admin.action(
        description="علامت‌گذاری به‌عنوان فروخته‌شده",
    )
    def mark_selected_as_sold(
        self,
        request,
        queryset,
    ):
        updated_count = queryset.update(
            availability_status=(
                Property.AvailabilityStatus.SOLD
            ),
            updated_at=timezone.now(),
        )

        self.message_user(
            request,
            f"{updated_count} ملک فروخته‌شده ثبت شد.",
            level=messages.SUCCESS,
        )

    @admin.action(
        description="علامت‌گذاری به‌عنوان اجاره‌رفته",
    )
    def mark_selected_as_rented(
        self,
        request,
        queryset,
    ):
        updated_count = queryset.update(
            availability_status=(
                Property.AvailabilityStatus.RENTED
            ),
            updated_at=timezone.now(),
        )

        self.message_user(
            request,
            f"{updated_count} ملک اجاره‌رفته ثبت شد.",
            level=messages.SUCCESS,
        )

    @admin.action(
        description="علامت‌گذاری به‌عنوان موقتاً غیرفعال",
    )
    def mark_selected_as_unavailable(
        self,
        request,
        queryset,
    ):
        updated_count = queryset.update(
            availability_status=(
                Property.AvailabilityStatus.UNAVAILABLE
            ),
            updated_at=timezone.now(),
        )

        self.message_user(
            request,
            f"{updated_count} ملک موقتاً غیرفعال شد.",
            level=messages.SUCCESS,
        )


@admin.register(PropertyImage)
class PropertyImageAdmin(admin.ModelAdmin):

    form = PropertyImageAdminForm

    class Media:
        css = {
            "all": (
                "core/css/admin_custom.css",
            )
        }

    list_display = (
        "property",
        "is_cover",
        "display_order",
        "created_at",
    )

    list_filter = (
        "is_cover",
    )

    search_fields = (
        "property__reference_code",
        "property__title",
        "alt_text",
    )

    autocomplete_fields = (
        "property",
    )

    ordering = (
        "-is_cover",
        "display_order",
        "created_at",
    )

    list_select_related = (
        "property",
    )

    list_per_page = 30