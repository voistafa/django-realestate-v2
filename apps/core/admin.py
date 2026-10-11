from django import forms
from django.contrib import admin
from jalali_date.admin import ModelAdminJalaliMixin


class PriceInput(forms.NumberInput):
    def format_value(self, value):
        if value:
            return f"{value:,}"
        return value


class BaseAdmin(
    ModelAdminJalaliMixin,
    admin.ModelAdmin,
):
    def format_price(self, value):
        if value:
            return f"{value:,}"
        return value

    def formfield_for_dbfield(self, db_field, request, **kwargs):
        formfield = super().formfield_for_dbfield(
            db_field,
            request,
            **kwargs,
        )

        if db_field.get_internal_type() in (
            "DecimalField",
            "IntegerField",
            "PositiveIntegerField",
        ):
            if formfield:
                formfield.widget.attrs.update(
                    {
                        "class": "price-field",
                    }
                )

        return formfield


def fa_digits(value):
    """
    تبدیل اعداد انگلیسی به فارسی
    """
    if not isinstance(value, str):
        value = str(value)

    return value.translate(
        str.maketrans(
            "0123456789",
            "۰۱۲۳۴۵۶۷۸۹",
        )
    )


admin.site.site_header = "مدیریت کلارخانه"
admin.site.site_title = "مدیریت کلارخانه"
admin.site.index_title = "مدیریت وبگاه"