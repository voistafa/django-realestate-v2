(function () {
    "use strict";

    function start() {
        const latitude = document.getElementById("id_latitude");
        const longitude = document.getElementById("id_longitude");

        if (!latitude || !longitude) {
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

        function sanitize(value, maxIntegerDigits) {
            value = toLatinDigits(value)
                .replace(/[٫,]/g, ".")
                .replace(/[^0-9.-]/g, "");

            const isNegative = value.startsWith("-");

            value = value.replace(/-/g, "");

            const hasDecimalPoint = value.includes(".");
            const parts = value.split(".");

            let integerPart = parts[0]
                .slice(0, maxIntegerDigits);

            const decimalPart = parts
                .slice(1)
                .join("")
                .slice(0, 6);

            let result = integerPart;

            if (hasDecimalPoint) {
                result += "." + decimalPart;
            }

            if (isNegative) {
                result = "-" + result;
            }

            return result;
        }

        function configure(
            input,
            min,
            max,
            maxIntegerDigits,
            label,
            maxLength
        ) {
            input.type = "text";
            input.inputMode = "decimal";
            input.autocomplete = "off";
            input.dir = "ltr";
            input.maxLength = maxLength;

            input.dataset.lastValid = input.value || "";

            input.addEventListener("input", function () {
                const sanitized = sanitize(
                    input.value,
                    maxIntegerDigits
                );

                if (
                    sanitized === ""
                    || sanitized === "-"
                    || sanitized === "."
                    || sanitized === "-."
                ) {
                    input.value = sanitized;
                    input.dataset.lastValid = sanitized;
                    input.setCustomValidity("");
                    return;
                }

                const number = Number(sanitized);

                if (
                    Number.isFinite(number)
                    && number >= min
                    && number <= max
                ) {
                    input.value = sanitized;
                    input.dataset.lastValid = sanitized;
                    input.setCustomValidity("");
                    return;
                }

                input.value = input.dataset.lastValid || "";
            });

            input.addEventListener("blur", function () {
                if (!input.value) {
                    input.setCustomValidity("");
                    return;
                }

                const number = Number(input.value);

                if (
                    !Number.isFinite(number)
                    || number < min
                    || number > max
                ) {
                    input.setCustomValidity(
                        `${label} باید عددی بین ${min} و ${max} باشد.`
                    );
                    input.reportValidity();
                    return;
                }

                input.setCustomValidity("");
            });
        }

        configure(
            latitude,
            -90,
            90,
            2,
            "عرض جغرافیایی",
            10
        );

        configure(
            longitude,
            -180,
            180,
            3,
            "طول جغرافیایی",
            11
        );

        const form = latitude.closest("form");

        if (form) {
            form.addEventListener("submit", function (event) {
                const hasLatitude = latitude.value !== "";
                const hasLongitude = longitude.value !== "";

                latitude.setCustomValidity("");
                longitude.setCustomValidity("");

                if (hasLatitude !== hasLongitude) {
                    event.preventDefault();

                    const message =
                        "عرض و طول جغرافیایی باید هر دو باهم ثبت شوند.";

                    latitude.setCustomValidity(message);
                    longitude.setCustomValidity(message);

                    latitude.reportValidity();
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