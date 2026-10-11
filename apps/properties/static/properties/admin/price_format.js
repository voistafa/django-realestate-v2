(function () {
    "use strict";

    function toEnglishDigits(value) {
        return value.replace(/[۰-۹]/g, function (digit) {
            return "0123456789"[
                "۰۱۲۳۴۵۶۷۸۹".indexOf(digit)
            ];
        });
    }


    function toPersianDigits(value) {
        return value.replace(/[0-9]/g, function (digit) {
            return "۰۱۲۳۴۵۶۷۸۹"[digit];
        });
    }


    function formatPrice(value) {
        let number = toEnglishDigits(value);

        number = number.replace(/,/g, "");

        if (!number) {
            return "";
        }

        number = Number(number).toLocaleString("en-US");

        return toPersianDigits(number);
    }


    function initializePriceFields() {
        document
            .querySelectorAll(".price-field")
            .forEach(function (input) {

                if (input.dataset.priceReady) {
                    return;
                }

                input.dataset.priceReady = "true";

                input.value = formatPrice(input.value);

                input.addEventListener(
                    "input",
                    function () {
                        const cursor = input.selectionStart;

                        input.value = formatPrice(
                            input.value
                        );

                        input.setSelectionRange(
                            cursor,
                            cursor
                        );
                    }
                );
            });
    }


    document.addEventListener(
        "submit",
        function () {
            document
                .querySelectorAll(".price-field")
                .forEach(function (input) {
                    input.value = toEnglishDigits(
                        input.value.replace(/,/g, "")
                    );
                });
        }
    );


    document.addEventListener(
        "DOMContentLoaded",
        initializePriceFields
    );

})();