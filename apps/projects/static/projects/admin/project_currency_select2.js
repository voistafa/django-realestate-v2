(function ($) {
    "use strict";

    function start() {
        const $select = $("#id_currency_code");
        const priceInput = document.getElementById(
            "id_starting_price"
        );

        if (
            !$select.length ||
            !priceInput ||
            typeof $.fn.select2 !== "function"
        ) {
            return;
        }

        if (!$select.hasClass("select2-hidden-accessible")) {
            $select.select2({
                minimumResultsForSearch: Infinity,
                dir: "rtl",
                dropdownCssClass:
                    "project-currency-select2-dropdown"
            });
        }

        const container = $select
            .next(".select2-container")[0];

        if (!container) {
            return;
        }

        container.classList.add(
            "project-currency-select2"
        );

        const selection = container.querySelector(
            ".select2-selection--single"
        );

        const rendered = container.querySelector(
            ".select2-selection__rendered"
        );

        function syncWithPriceInput() {
            if (!selection || !rendered) {
                return;
            }

            const style = window.getComputedStyle(
                priceInput
            );

            const rect =
                priceInput.getBoundingClientRect();

            container.style.width =
                rect.width + "px";

            selection.style.height =
                rect.height + "px";

            selection.style.minHeight =
                rect.height + "px";

            selection.style.backgroundColor =
                style.backgroundColor;

            selection.style.border =
                style.border;

            selection.style.borderRadius =
                style.borderRadius;

            selection.style.boxSizing =
                "border-box";

            selection.style.fontFamily =
                style.fontFamily;

            selection.style.fontSize =
                style.fontSize;

            selection.style.fontWeight =
                style.fontWeight;

            selection.style.color =
                style.color;

            rendered.style.fontFamily =
                style.fontFamily;

            rendered.style.fontSize =
                style.fontSize;

            rendered.style.fontWeight =
                style.fontWeight;

            rendered.style.color =
                style.color;
        }

        syncWithPriceInput();

        window.addEventListener(
            "resize",
            syncWithPriceInput
        );

        $select.on(
            "select2:open",
            function () {
                window.requestAnimationFrame(
                    function () {
                        const dropdown =
                            document.querySelector(
                                ".project-currency-select2-dropdown"
                            );

                        if (!dropdown) {
                            return;
                        }

                        const style =
                            window.getComputedStyle(
                                priceInput
                            );

                        dropdown.style.fontFamily =
                            style.fontFamily;

                        dropdown.style.fontSize =
                            style.fontSize;
                    }
                );
            }
        );
    }

    $(start);

}(django.jQuery));