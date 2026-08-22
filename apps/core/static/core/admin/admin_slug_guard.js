(function () {
    "use strict";

    function initializeSlugFields() {
        const slugInputs = document.querySelectorAll(
            'input[name="slug"], input[name$="-slug"]'
        );

        slugInputs.forEach(function (input) {
            input.setAttribute("dir", "ltr");
            input.setAttribute("autocomplete", "off");
            input.setAttribute(
                "pattern",
                "[A-Za-z0-9]+(?:-[A-Za-z0-9]+)*"
            );

            input.addEventListener("input", function () {
                let value = input.value;

                // فقط حروف انگلیسی، عدد و خط تیره
                value = value.replace(/[^A-Za-z0-9-]/g, "");

                // جلوگیری از چند خط تیره پشت سر هم
                value = value.replace(/-+/g, "-");

                // تبدیل حروف انگلیسی به lowercase
                value = value.toLowerCase();

                input.value = value;
            });
        });
    }

    if (document.readyState === "loading") {
        document.addEventListener(
            "DOMContentLoaded",
            initializeSlugFields,
            { once: true }
        );
    } else {
        initializeSlugFields();
    }
}());