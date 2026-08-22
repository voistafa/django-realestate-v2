(function () {
    "use strict";

    function start() {
        const input = document.getElementById("id_published_at_1");

        if (!input) {
            return;
        }

        const persianDigits = "۰۱۲۳۴۵۶۷۸۹";
        const arabicDigits = "٠١٢٣٤٥٦٧٨٩";

        function toLatinDigits(value) {
            return String(value)
                .replace(/[۰-۹]/g, function (digit) {
                    return String(persianDigits.indexOf(digit));
                })
                .replace(/[٠-٩]/g, function (digit) {
                    return String(arabicDigits.indexOf(digit));
                });
        }

        function getDigits(value) {
            return toLatinDigits(value)
                .replace(/[^0-9]/g, "")
                .slice(0, 4);
        }

        function isValidPartial(digits) {
            if (digits.length >= 1 && Number(digits[0]) > 2) {
                return false;
            }

            if (
                digits.length >= 2
                && Number(digits.slice(0, 2)) > 23
            ) {
                return false;
            }

            if (
                digits.length >= 3
                && Number(digits[2]) > 5
            ) {
                return false;
            }

            return true;
        }

        function formatDigits(digits) {
            if (digits.length === 0) {
                return "";
            }

            if (digits.length === 1) {
                return digits;
            }

            if (digits.length === 2) {
                return digits + ":";
            }

            return (
                digits.slice(0, 2)
                + ":"
                + digits.slice(2, 4)
            );
        }

        function validateFinalValue() {
            if (input.value === "") {
                input.setCustomValidity("");
                return true;
            }

            const valid = /^([01][0-9]|2[0-3]):[0-5][0-9]$/.test(
                input.value
            );

            input.setCustomValidity(
                valid
                    ? ""
                    : "زمان را به‌صورت کامل مانند 14:30 وارد کنید."
            );

            return valid;
        }

        input.type = "text";
        input.placeholder = "--:--";
        input.maxLength = 5;
        input.inputMode = "numeric";
        input.autocomplete = "off";
        input.dir = "ltr";

        input.dataset.lastValid = input.value || "";

        input.addEventListener("input", function () {
            const digits = getDigits(input.value);

            if (!isValidPartial(digits)) {
                input.value = input.dataset.lastValid;
                return;
            }

            input.value = formatDigits(digits);
            input.dataset.lastValid = input.value;
            input.setCustomValidity("");

            input.setSelectionRange(
                input.value.length,
                input.value.length
            );
        });

        input.addEventListener("keydown", function (event) {
            if (
                event.key === "Backspace"
                && input.value.endsWith(":")
            ) {
                event.preventDefault();

                const digits = getDigits(input.value).slice(0, -1);

                input.value = formatDigits(digits);
                input.dataset.lastValid = input.value;
            }
        });

        input.addEventListener("blur", validateFinalValue);

        const form = input.closest("form");

        if (form) {
            form.addEventListener("submit", function (event) {
                if (!validateFinalValue()) {
                    event.preventDefault();
                    input.reportValidity();
                }
            });
        }
    }

    if (document.readyState === "loading") {
        document.addEventListener(
            "DOMContentLoaded",
            start,
            { once: true }
        );
    } else {
        start();
    }
}());