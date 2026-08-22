(function () {
    "use strict";

    const ENGLISH_DIGITS = "0123456789";
    const PERSIAN_DIGITS = "۰۱۲۳۴۵۶۷۸۹";

    function toPersianDigits(value) {
        return String(value).replace(/[0-9]/g, function (digit) {
            return PERSIAN_DIGITS[ENGLISH_DIGITS.indexOf(digit)];
        });
    }

    function toEnglishDigits(value) {
        return String(value).replace(/[۰-۹]/g, function (digit) {
            return ENGLISH_DIGITS[PERSIAN_DIGITS.indexOf(digit)];
        });
    }

    function isPhoneField(input) {
        if (!(input instanceof HTMLInputElement)) {
            return false;
        }

        const name = (input.name || "").toLowerCase();

        return (
            input.type === "tel" ||
            name === "phone" ||
            name.includes("phone")
        );
    }

    function preparePhoneField(input) {
        if (!isPhoneField(input)) {
            return;
        }

        input.value = toPersianDigits(input.value);

        input.setAttribute("inputmode", "tel");
        input.setAttribute("dir", "ltr");

        input.addEventListener("input", function () {
            const cursorPosition = input.selectionStart;

            input.value = toPersianDigits(input.value);

            if (cursorPosition !== null) {
                input.setSelectionRange(
                    cursorPosition,
                    cursorPosition
                );
            }
        });
    }

    function prepareAllPhoneFields(root) {
        root.querySelectorAll("input").forEach(preparePhoneField);
    }

    function normalizeBeforeSubmit(form) {
        form.querySelectorAll("input").forEach(function (input) {
            if (isPhoneField(input)) {
                input.value = toEnglishDigits(input.value);
            }
        });
    }

    function initialize() {
        prepareAllPhoneFields(document);

        document.querySelectorAll("form").forEach(function (form) {
            form.addEventListener("submit", function () {
                normalizeBeforeSubmit(form);
            });
        });
    }

    if (document.readyState === "loading") {
        document.addEventListener(
            "DOMContentLoaded",
            initialize,
            { once: true }
        );
    } else {
        initialize();
    }
}());