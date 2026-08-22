from django import forms
from django.contrib import admin, messages
from django.core.exceptions import ValidationError
from django.utils import timezone
from jalali_date import datetime2jalali
from jalali_date.fields import (
    JalaliDateField,
    SplitJalaliDateTimeField,
)
from jalali_date.widgets import (
    AdminJalaliDateWidget,
    AdminSplitJalaliDateTime,
)

from .models import (
    DevelopmentProject,
    ProjectFeature,
    ProjectImage,
)


PERSIAN_DIGITS_TRANSLATION = str.maketrans(
    "0123456789",
    "۰۱۲۳۴۵۶۷۸۹",
)

PERSIAN_TO_LATIN_DIGITS = str.maketrans(
    "۰۱۲۳۴۵۶۷۸۹٠١٢٣٤٥٦٧٨٩",
    "01234567890123456789",
)


class PersianFriendlyTimeField(forms.TimeField):
    """Accept Persian/Arabic digits while keeping Django validation."""

    def to_python(self, value):
        if isinstance(value, str):
            value = value.translate(
                PERSIAN_TO_LATIN_DIGITS,
            ).strip()

        return super().to_python(value)


class CompletionPercentageField(forms.IntegerField):
    """Accept only a whole percentage between 0 and 100."""

    def to_python(self, value):
        if isinstance(value, str):
            value = value.translate(
                PERSIAN_TO_LATIN_DIGITS,
            ).strip()

        return super().to_python(value)


def to_persian_digits(value):
    if value in (None, ""):
        return "—"

    return str(value).translate(
        PERSIAN_DIGITS_TRANSLATION,
    )


def format_jalali_datetime(value):
    if value is None:
        return "—"

    localized_value = timezone.localtime(value)
    jalali_value = datetime2jalali(localized_value)

    return to_persian_digits(
        jalali_value.strftime(
            "%Y/%m/%d - %H:%M",
        ),
    )


class DevelopmentProjectAdminForm(forms.ModelForm):
    completion_percentage = CompletionPercentageField(
        label="درصد پیشرفت",
        min_value=0,
        max_value=100,
        localize=False,
        error_messages={
            "required": "وارد کردن درصد پیشرفت الزامی است.",
            "invalid": "درصد پیشرفت باید یک عدد صحیح باشد.",
            "min_value": "درصد پیشرفت نمی‌تواند کمتر از ۰ باشد.",
            "max_value": "درصد پیشرفت نمی‌تواند بیشتر از ۱۰۰ باشد.",
        },
        widget=forms.TextInput(
            attrs={
                "class": "vIntegerField",
                "style": (
                    "width: 96px !important;"
                    "min-width: 96px !important;"
                    "max-width: 96px !important;"
                    "text-align: center;"
                    "box-sizing: border-box;"
                ),
                "maxlength": "3",
                "inputmode": "numeric",
                "pattern": "(?:100|[0-9۰-۹٠-٩]{1,2})",
                "autocomplete": "off",
                "dir": "ltr",
                "aria-label": "درصد پیشرفت",
                "onfocus": (
                    "this.dataset.lastValid=this.value;"
                ),
                "oninput": (
                    "const digitMap={"
                    "'۰':'0','۱':'1','۲':'2','۳':'3','۴':'4',"
                    "'۵':'5','۶':'6','۷':'7','۸':'8','۹':'9',"
                    "'٠':'0','١':'1','٢':'2','٣':'3','٤':'4',"
                    "'٥':'5','٦':'6','٧':'7','٨':'8','٩':'9'"
                    "};"
                    "let value=this.value"
                    ".replace(/[۰-۹٠-٩]/g,function(digit){"
                    "return digitMap[digit];"
                    "})"
                    ".replace(/[^0-9]/g,'');"
                    "if(value===''){"
                    "this.value='';"
                    "this.dataset.lastValid='';"
                    "}else if(/^(?:[0-9]{1,2}|100)$/.test(value)){"
                    "this.value=value;"
                    "this.dataset.lastValid=value;"
                    "}else{"
                    "this.value=this.dataset.lastValid||'';"
                    "}"
                ),
                "onblur": (
                    "if(this.value!==''){"
                    "this.value=String(Number(this.value));"
                    "this.dataset.lastValid=this.value;"
                    "}"
                ),
            },
        ),
    )

    start_date = JalaliDateField(
        label="تاریخ شروع",
        required=False,
        widget=AdminJalaliDateWidget(
            attrs={
                "data-jdp": "",
                "readonly": "readonly",
                "autocomplete": "off",
                "inputmode": "none",
            },
        ),
    )

    expected_completion_date = JalaliDateField(
        label="تاریخ تقریبی تحویل",
        required=False,
        widget=AdminJalaliDateWidget(
            attrs={
                "data-jdp": "",
                "readonly": "readonly",
                "autocomplete": "off",
                "inputmode": "none",
            },
        ),
    )

    published_at = SplitJalaliDateTimeField(
        label="تاریخ و زمان انتشار",
        required=False,
        widget=AdminSplitJalaliDateTime,
    )

    class Meta:
        model = DevelopmentProject
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        features_field = self.fields["features"]
        features_field.label = "امکانات پروژه"

        features_widget = features_field.widget

        if hasattr(features_widget, "widget"):
            features_widget = features_widget.widget

        if hasattr(features_widget, "verbose_name"):
            features_widget.verbose_name = "امکانات پروژه"

        published_field = self.fields["published_at"]
        published_widget = published_field.widget

        if hasattr(published_field, "fields"):
            subfields = list(published_field.fields)

            subfields[1] = PersianFriendlyTimeField(
                required=False,
                input_formats=("%H:%M",),
            )

            published_field.fields = tuple(subfields)

        if hasattr(published_widget, "widgets"):
            date_widget = published_widget.widgets[0]
            time_widget = published_widget.widgets[1]

            date_classes = date_widget.attrs.get(
                "class",
                "",
            )

            date_widget.attrs.update(
                {
                    "class": (
                        f"{date_classes} "
                        "project-jalali-date-input"
                    ).strip(),
                    "data-jdp": "",
                    "readonly": "readonly",
                    "autocomplete": "off",
                    "inputmode": "none",
                },
            )

            time_classes = time_widget.attrs.get(
                "class",
                "",
            )

            time_widget.input_type = "text"
            time_widget.format = "%H:%M"

            time_widget.attrs.update(
                {
                    "class": (
                        f"{time_classes} "
                        "project-time-input"
                    ).strip(),
                    "placeholder": "--:--",
                    "maxlength": "5",
                    "autocomplete": "off",
                    "inputmode": "numeric",
                    "dir": "ltr",
                    "aria-label": "زمان انتشار",
                },
            )

    def clean_published_at(self):
        published_at = self.cleaned_data.get(
            "published_at",
        )

        if published_at is None:
            return None

        return published_at.replace(
            second=0,
            microsecond=0,
        )

    def clean_publication_status(self):
        status = self.cleaned_data.get(
            "publication_status",
        )

        if (
            status
            == DevelopmentProject.PublicationStatus.PUBLISHED
            and (
                self.instance.pk is None
                or self.instance.publication_status
                != DevelopmentProject.PublicationStatus.PUBLISHED
            )
        ):
            raise forms.ValidationError(
                "برای انتشار، ابتدا پروژه و تصویر کاور را ذخیره کنید؛ "
                "سپس از عملیات «انتشار پروژه‌های انتخاب‌شده» استفاده کنید."
            )

        return status


@admin.register(ProjectFeature)
class ProjectFeatureAdmin(admin.ModelAdmin):
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


class ProjectImageInline(admin.TabularInline):
    model = ProjectImage
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


@admin.register(DevelopmentProject)
class DevelopmentProjectAdmin(admin.ModelAdmin):
    form = DevelopmentProjectAdminForm

    list_display = (
        "reference_code",
        "title",
        "region",
        "construction_status",
        "publication_status",
        "completion_percentage",
        "starting_price",
        "price_on_request",
        "currency_code",
        "is_featured",
        "published_at_jalali",
    )

    list_filter = (
        "publication_status",
        "construction_status",
        "is_featured",
        "price_on_request",
        "currency_code",
        "region__city",
        "region",
        "agent",
    )

    search_fields = (
        "reference_code",
        "title",
        "slug",
        "developer_name",
        "short_description",
        "description",
        "public_location",
        "private_address",
        "region__name",
        "region__city__name",
        "agent__full_name",
    )

    prepopulated_fields = {
        "slug": (
            "title",
        ),
    }

    autocomplete_fields = (
        "region",
        "agent",
    )

    filter_horizontal = (
        "features",
    )

    list_select_related = (
        "region",
        "region__city",
        "agent",
    )

    readonly_fields = (
        "created_at_jalali",
        "updated_at_jalali",
    )

    fieldsets = (
        (
            "اطلاعات اصلی پروژه",
            {
                "fields": (
                    "reference_code",
                    "title",
                    "slug",
                ),
            },
        ),
        (
            "منطقه و مسئول پروژه",
            {
                "fields": (
                    "region",
                    "agent",
                    "developer_name",
                    "features",
                ),
            },
        ),
        (
            "وضعیت پروژه",
            {
                "fields": (
                    (
                        "construction_status",
                        "publication_status",
                    ),
                    (
                        "completion_percentage",
                        "is_featured",
                    ),
                    "published_at",
                ),
            },
        ),
        (
            "توضیحات",
            {
                "fields": (
                    "short_description",
                    "description",
                ),
            },
        ),
        (
            "موقعیت عمومی",
            {
                "fields": (
                    "public_location",
                    (
                        "latitude",
                        "longitude",
                    ),
                    "is_exact_location_public",
                ),
            },
        ),
        (
            "اطلاعات خصوصی",
            {
                "fields": (
                    "private_address",
                ),
                "description": (
                    "اطلاعات این بخش فقط برای استفاده داخلی "
                    "مجموعه است و نباید در سایت عمومی نمایش داده شود."
                ),
                "classes": (
                    "collapse",
                ),
            },
        ),
        (
            "قیمت پروژه",
            {
                "fields": (
                    (
                        "starting_price",
                        "currency_code",
                    ),
                    "price_on_request",
                ),
            },
        ),
        (
            "واحدها و زمان‌بندی",
            {
                "fields": (
                    (
                        "total_units",
                        "available_units",
                    ),
                    (
                        "start_date",
                        "expected_completion_date",
                    ),
                ),
            },
        ),
        (
            "اطلاعات سیستمی",
            {
                "fields": (
                    "created_at_jalali",
                    "updated_at_jalali",
                ),
                "classes": (
                    "collapse",
                ),
            },
        ),
    )

    ordering = (
        "-published_at",
        "-created_at",
    )

    actions = (
        "publish_selected_projects",
        "move_selected_projects_to_draft",
        "archive_selected_projects",
    )

    inlines = (
        ProjectImageInline,
    )

    list_per_page = 25
    save_on_top = True

    @admin.display(
        description="تاریخ و زمان انتشار",
        ordering="published_at",
    )
    def published_at_jalali(self, obj):
        return format_jalali_datetime(
            obj.published_at,
        )

    @admin.display(
        description="تاریخ و زمان ایجاد",
        ordering="created_at",
    )
    def created_at_jalali(self, obj):
        if obj is None or obj.pk is None:
            return "—"

        return format_jalali_datetime(
            obj.created_at,
        )

    @admin.display(
        description="تاریخ و زمان آخرین ویرایش",
        ordering="updated_at",
    )
    def updated_at_jalali(self, obj):
        if obj is None or obj.pk is None:
            return "—"

        return format_jalali_datetime(
            obj.updated_at,
        )

    def save_model(
        self,
        request,
        obj,
        form,
        change,
    ):
        if (
            obj.publication_status
            == DevelopmentProject.PublicationStatus.PUBLISHED
            and obj.published_at is None
        ):
            obj.published_at = timezone.now().replace(
                second=0,
                microsecond=0,
            )

        elif (
            obj.publication_status
            == DevelopmentProject.PublicationStatus.DRAFT
        ):
            obj.published_at = None

        super().save_model(
            request,
            obj,
            form,
            change,
        )

    @admin.action(
        description="انتشار پروژه‌های انتخاب‌شده",
    )
    def publish_selected_projects(
        self,
        request,
        queryset,
    ):
        published_count = 0
        failed_projects = []

        for project in queryset:
            try:
                project.publish()
                published_count += 1

            except ValidationError:
                failed_projects.append(
                    project.reference_code,
                )

        if published_count:
            self.message_user(
                request,
                (
                    f"{published_count} پروژه "
                    "با موفقیت منتشر شد."
                ),
                level=messages.SUCCESS,
            )

        if failed_projects:
            failed_codes = "، ".join(
                failed_projects[:10],
            )

            self.message_user(
                request,
                (
                    "برخی پروژه‌ها به‌دلیل اطلاعات ناقص "
                    f"منتشر نشدند: {failed_codes}"
                ),
                level=messages.WARNING,
            )

    @admin.action(
        description="انتقال پروژه‌های انتخاب‌شده به پیش‌نویس",
    )
    def move_selected_projects_to_draft(
        self,
        request,
        queryset,
    ):
        updated_count = queryset.update(
            publication_status=(
                DevelopmentProject.PublicationStatus.DRAFT
            ),
            published_at=None,
            updated_at=timezone.now(),
        )

        self.message_user(
            request,
            (
                f"{updated_count} پروژه "
                "به پیش‌نویس منتقل شد."
            ),
            level=messages.SUCCESS,
        )

    @admin.action(
        description="بایگانی پروژه‌های انتخاب‌شده",
    )
    def archive_selected_projects(
        self,
        request,
        queryset,
    ):
        updated_count = queryset.update(
            publication_status=(
                DevelopmentProject.PublicationStatus.ARCHIVED
            ),
            updated_at=timezone.now(),
        )

        self.message_user(
            request,
            (
                f"{updated_count} پروژه "
                "بایگانی شد."
            ),
            level=messages.SUCCESS,
        )

    class Media:
        css = {
            "all": (
                (
                    "admin/jquery.ui.datepicker.jalali/"
                    "themes/base/jquery-ui.min.css"
                ),
                "projects/admin/project_form.css",
                (
                    "projects/admin/"
                    "project_admin_refinements_v2.css"
                ),
                (
                    "projects/admin/"
                    "project_currency_select2.css"
                ),
            ),
        }

        js = (
            "projects/admin/project_time_input.js",
            "projects/admin/project_coordinates_input.js",
            "projects/admin/project_price_input.js",
            "projects/admin/project_currency_select2.js",
        )


@admin.register(ProjectImage)
class ProjectImageAdmin(admin.ModelAdmin):
    list_display = (
        "project",
        "is_cover",
        "display_order",
        "created_at",
    )

    list_filter = (
        "is_cover",
    )

    search_fields = (
        "project__reference_code",
        "project__title",
        "alt_text",
    )

    autocomplete_fields = (
        "project",
    )

    ordering = (
        "-is_cover",
        "display_order",
        "created_at",
    )

    list_per_page = 30