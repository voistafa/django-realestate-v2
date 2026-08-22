from django import forms


class RubikaAdminField(forms.CharField):
    """
    فیلد آزاد روبیکا در Django Admin.

    مقدار واردشده بدون تبدیل خودکار ذخیره می‌شود.
    """

    def __init__(self, *args, **kwargs):
        kwargs["widget"] = forms.TextInput(
            attrs={
                "placeholder": "VOISTAFA یا @VOISTAFA یا لینک روبیکا",
                "dir": "ltr",
                "autocomplete": "off",
                "spellcheck": "false",
            }
        )

        kwargs["help_text"] = ""
        kwargs["strip"] = False

        super().__init__(*args, **kwargs)


class RubikaAdminMixin:
    """
    نمایش ساده فیلد rubika_url در Django Admin
    بدون اعتبارسنجی URL و بدون تغییر مقدار.
    """

    def formfield_for_dbfield(
        self,
        db_field,
        request,
        **kwargs,
    ):
        if db_field.name == "rubika_url":
            kwargs["form_class"] = RubikaAdminField

            kwargs["widget"] = forms.TextInput(
                attrs={
                    "placeholder": "VOISTAFA یا @VOISTAFA یا لینک روبیکا",
                    "dir": "ltr",
                    "autocomplete": "off",
                    "spellcheck": "false",
                }
            )

            kwargs["help_text"] = ""

        return super().formfield_for_dbfield(
            db_field,
            request,
            **kwargs,
        )