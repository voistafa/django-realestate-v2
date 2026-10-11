(function () {
    "use strict";

    const ENGLISH_DIGITS = "0123456789";
    const PERSIAN_DIGITS = "۰۱۲۳۴۵۶۷۸۹";

    function toPersianDigits(value) {
        return String(value).replace(/[0-9]/g, function (digit) {
            return PERSIAN_DIGITS[
                ENGLISH_DIGITS.indexOf(digit)
            ];
        });
    }

    function convertTextNodes(root) {
        const walker = document.createTreeWalker(
            root,
            NodeFilter.SHOW_TEXT
        );

        const nodes = [];

        while (walker.nextNode()) {
            nodes.push(walker.currentNode);
        }

        nodes.forEach(function (node) {
            if (
                node.parentElement &&
                node.parentElement.closest(
                    "script, style, input, textarea"
                )
            ) {
                return;
            }

            node.nodeValue = toPersianDigits(
                node.nodeValue
            );
        });
    }

    function initialize() {
        const adminContent =
            document.querySelector("#content");

        if (adminContent) {
            convertTextNodes(adminContent);
        }
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