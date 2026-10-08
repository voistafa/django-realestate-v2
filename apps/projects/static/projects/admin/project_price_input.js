(function () {
    "use strict";

    console.log("project_price_input loaded");

    function start() {
        const input = document.getElementById("id_starting_price");

        if (!input) {
            return;
        }

        function toEnglishDigits(value) {
            return String(value)
                .replace(/[۰-۹]/g, function (digit) {
                    return "0123456789"["۰۱۲۳۴۵۶۷۸۹".indexOf(digit)];
                })
                .replace(/[٠-٩]/g, function (digit) {
                    return "0123456789"["٠١٢٣٤٥٦٧٨٩".indexOf(digit)];
                });
        }


        function toPersianDigits(value) {
            return String(value).replace(/[0-9]/g, function (digit) {
                return "۰۱۲۳۴۵۶۷۸۹"[digit];
            });
        }


        function formatPrice(value) {
            let number = toEnglishDigits(value);

            number = number.replace(/,/g, "");

            number = number.replace(/[^0-9]/g, "");

            if (!number) {
                return "";
            }

            number = Number(number).toLocaleString("en-US");

            return toPersianDigits(number);
        }


        function rawValue(value) {
            return toEnglishDigits(
                value.replace(/,/g, "")
            );
        }


        input.type = "text";
        input.inputMode = "numeric";

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
                input.value = rawValue(input.value);
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

})();