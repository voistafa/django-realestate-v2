from django import template

register = template.Library()

ENGLISH_DIGITS = "0123456789"
PERSIAN_DIGITS = "۰۱۲۳۴۵۶۷۸۹"


@register.filter
def fa_digits(value):
    if value is None:
        return ""

    return str(value).translate(
        str.maketrans(ENGLISH_DIGITS, PERSIAN_DIGITS)
    )
