(function () {
    "use strict";

    function start() {
        const input = document.getElementById("id_starting_price");

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
                .slice(0, 20);
        }

        function formatPrice(value) {
            const digits = getDigits(value);

            if (!digits) {
                return "";
            }

            return digits.replace(
                /\B(?=(\d{3})+(?!\d))/g,
                "٬"
            );
        }

        input.type = "text";
        input.inputMode = "numeric";
        input.autocomplete = "off";
        input.dir = "ltr";

        input.value = formatPrice(input.value);

        input.addEventListener("input", function () {
            input.value = formatPrice(input.value);

            input.setSelectionRange(
                input.value.length,
                input.value.length
            );
        });

        const form = input.closest("form");

        if (form) {
            form.addEventListener("submit", function () {
                input.value = getDigits(input.value);
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