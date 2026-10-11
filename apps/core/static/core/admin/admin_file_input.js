
(function () {
    "use strict";


    function initializeFileInput(input) {

        if (
            input.dataset.customFileReady === "true"
        ) {
            return;
        }

        input.dataset.customFileReady = "true";


        let fileUpload =
            input.closest(".file-upload");


        if (!fileUpload) {

            fileUpload =
                input.parentElement;

        }


        const wrapper =
            document.createElement("div");

        wrapper.className =
            "admin-file-input";


        const label =
            document.createElement("span");

        label.className =
            "admin-file-input__label";

        label.textContent =
            "تغییر:";


        const button =
            document.createElement("button");

        button.type =
            "button";

        button.className =
            "admin-file-input__button";

        button.textContent =
            "انتخاب فایل";


        const filename =
            document.createElement("span");

        filename.className =
            "admin-file-input__name";

        filename.textContent =
            "فایلی انتخاب نشده است";


        input.style.display =
            "none";


        wrapper.appendChild(label);
        wrapper.appendChild(button);
        wrapper.appendChild(filename);


        input.parentNode.insertBefore(
            wrapper,
            input
        );


        wrapper.appendChild(input);


        button.addEventListener(
            "click",
            function () {
                input.click();
            }
        );


        input.addEventListener(
            "change",
            function () {

                if (
                    input.files &&
                    input.files.length > 0
                ) {

                    filename.textContent =
                        input.files[0].name;

                } else {

                    filename.textContent =
                        "فایلی انتخاب نشده است";

                }

            }
        );


        const oldTextNodes =
            Array.from(fileUpload.childNodes);


        oldTextNodes.forEach(
            function (node) {

                if (
                    node.nodeType === Node.TEXT_NODE &&
                    node.textContent.includes("تغییر:")
                ) {

                    node.textContent =
                        "";

                }

            }
        );

    }


    function initialize() {

        document.querySelectorAll(
            'input[type="file"]'
        ).forEach(
            initializeFileInput
        );

    }


    if (
        document.readyState === "loading"
    ) {

        document.addEventListener(
            "DOMContentLoaded",
            initialize,
            {
                once: true
            }
        );

    } else {

        initialize();

    }


    document.addEventListener(
        "formset:added",
        function (event) {

            event.detail.form
                .querySelectorAll(
                    'input[type="file"]'
                )
                .forEach(
                    initializeFileInput
                );

        }
    );


}());