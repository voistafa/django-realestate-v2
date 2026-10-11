(function () {
    "use strict";

    const translations = {
        "Add": "افزودن",
        "Change": "تغییر",
        "Delete": "حذف",
        "Save": "ذخیره",
        "Save and continue editing": "ذخیره و ادامه ویرایش",
        "Save and add another": "ذخیره و افزودن مورد جدید",
        "History": "تاریخچه",
        "View on site": "نمایش در سایت",
        "Log out": "خروج",
        "Password change": "تغییر گذرواژه",
        "Currently": "در حال حاضر",
        "Clear": "پاک کردن"
    };

    function translateTexts() {
        const walker = document.createTreeWalker(
            document.body,
            NodeFilter.SHOW_TEXT
        );

        const nodes = [];

        while (walker.nextNode()) {
            nodes.push(walker.currentNode);
        }

        nodes.forEach(function (node) {
            let text = node.nodeValue.trim();

            if (translations[text]) {
                node.nodeValue =
                    node.nodeValue.replace(
                        text,
                        translations[text]
                    );
            }
        });
    }

    function initialize() {
        translateTexts();
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