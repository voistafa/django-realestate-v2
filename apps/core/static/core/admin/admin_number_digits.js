(function () {
    "use strict";

    function prepareNumberFields() {
        document.querySelectorAll(
            "input[name='bedrooms'], input[name='bathrooms'], input[name='parking_spaces'], input[name='year_built'], input[name='floor_number'], input[name='total_floors']"
        ).forEach(function (input) {

            input.setAttribute("dir", "rtl");
            input.style.fontVariantNumeric = "normal";

        });
    }

    if (document.readyState === "loading") {
        document.addEventListener(
            "DOMContentLoaded",
            prepareNumberFields,
            { once: true }
        );
    } else {
        prepareNumberFields();
    }

})();