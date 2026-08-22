(function () {
    "use strict";

    const translations = new Map([
        [
            "Please correct the error below.",
            "لطفاً خطای مشخص‌شده در فرم را اصلاح کنید."
        ],
        [
            "Please correct the errors below.",
            "لطفاً خطاهای مشخص‌شده در فرم را اصلاح کنید."
        ]
    ]);

    const persianReplacements = new Map([
        ["آنرا", "آن را"],
        ["میتوانید", "می‌توانید"]
    ]);

    function normalizeText(value) {
        return value
            .replace(/\s+/g, " ")
            .trim();
    }

    function replacePersianText(rootElement) {
        const walker = document.createTreeWalker(
            rootElement,
            NodeFilter.SHOW_TEXT
        );

        const textNodes = [];

        while (walker.nextNode()) {
            textNodes.push(walker.currentNode);
        }

        textNodes.forEach(function (textNode) {
            let value = textNode.nodeValue;

            persianReplacements.forEach(function (correct, incorrect) {
                value = value.replaceAll(incorrect, correct);
            });

            textNode.nodeValue = value;
        });
    }

    function enhanceErrorNotes() {
        document.querySelectorAll(".errornote").forEach(function (element) {
            const text = normalizeText(element.textContent);

            if (translations.has(text)) {
                element.textContent = translations.get(text);
            }

            replacePersianText(element);

            element.classList.add(
                "admin-feedback",
                "admin-feedback--error"
            );

            element.setAttribute("role", "alert");
            element.setAttribute("aria-live", "assertive");
        });
    }

    function enhanceMessages() {
        document.querySelectorAll(".messagelist li").forEach(function (element) {
            replacePersianText(element);

            let level = "info";

            if (element.classList.contains("error")) {
                level = "error";
            } else if (element.classList.contains("warning")) {
                level = "warning";
            } else if (element.classList.contains("success")) {
                level = "success";
            }

            element.classList.add(
                "admin-feedback",
                "admin-feedback--" + level
            );

            if (level === "error") {
                element.setAttribute("role", "alert");
                element.setAttribute("aria-live", "assertive");
            } else {
                element.setAttribute("role", "status");
                element.setAttribute("aria-live", "polite");
            }
        });
    }

    function enhanceFieldErrors() {
        document.querySelectorAll(".errorlist").forEach(function (element) {
            replacePersianText(element);

            element.setAttribute("role", "alert");
            element.setAttribute("aria-live", "polite");
        });
    }

    function initializeFeedbackSystem() {
        enhanceErrorNotes();
        enhanceMessages();
        enhanceFieldErrors();
    }

    if (document.readyState === "loading") {
        document.addEventListener(
            "DOMContentLoaded",
            initializeFeedbackSystem,
            { once: true }
        );
    } else {
        initializeFeedbackSystem();
    }
}());