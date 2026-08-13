(function () {
    "use strict";

    const PERSIAN_DIGITS = "۰۱۲۳۴۵۶۷۸۹";

    const PERSIAN_MONTHS = [
        "فروردین",
        "اردیبهشت",
        "خرداد",
        "تیر",
        "مرداد",
        "شهریور",
        "مهر",
        "آبان",
        "آذر",
        "دی",
        "بهمن",
        "اسفند",
    ];

    function toPersianDigits(value) {
        return String(value).replace(
            /\d/g,
            function (digit) {
                return PERSIAN_DIGITS[
                    Number(digit)
                ];
            }
        );
    }

    function toLatinDigits(value) {
        return String(value)
            .replace(
                /[۰-۹]/g,
                function (digit) {
                    return String(
                        PERSIAN_DIGITS.indexOf(
                            digit
                        )
                    );
                }
            )
            .replace(
                /[٠-٩]/g,
                function (digit) {
                    return String(
                        "٠١٢٣٤٥٦٧٨٩".indexOf(
                            digit
                        )
                    );
                }
            );
    }

    function configureDatepicker() {
        const api = window.jalaliDatepicker;

        if (!api) {
            return false;
        }

        const options = {
            persianDigits: true,
            autoReadOnlyInput: true,
        };

        if (
            typeof api.updateOptions ===
            "function"
        ) {
            api.updateOptions(options);
            return true;
        }

        if (
            typeof api.startWatch ===
            "function"
        ) {
            api.startWatch(options);
            return true;
        }

        return false;
    }

    function looksLikeCalendar(element) {
        if (!(element instanceof Element)) {
            return false;
        }

        const className = String(
            element.className || ""
        ).toLowerCase();

        const text =
            element.textContent || "";

        const hasMonth =
            PERSIAN_MONTHS.some(
                function (month) {
                    return text.includes(month);
                }
            );

        const calendarClass = (
            className.includes("jdp")
            || className.includes("jalali")
            || className.includes("datepicker")
        );

        return hasMonth && (
            calendarClass
            || element.querySelectorAll(
                "select"
            ).length >= 2
        );
    }

    function findCalendarRoots() {
        const selectors = [
            ".jdp-container",
            ".jdp-wrapper",
            "[data-jdp-container]",
            "[class*='jdp']",
            "[class*='jalali']",
            "[class*='datepicker']",
        ].join(",");

        const candidates = Array.from(
            document.querySelectorAll(
                selectors
            )
        ).filter(looksLikeCalendar);

        Array.from(
            document.body.children
        ).forEach(
            function (child) {
                if (looksLikeCalendar(child)) {
                    candidates.push(child);
                }
            }
        );

        return candidates.filter(
            function (
                candidate,
                index,
                all
            ) {
                if (
                    all.indexOf(candidate)
                    !== index
                ) {
                    return false;
                }

                return !all.some(
                    function (other) {
                        return (
                            other !== candidate
                            && other.contains(
                                candidate
                            )
                        );
                    }
                );
            }
        );
    }

    function translateCalendar(calendar) {
        calendar.style.fontFamily = [
            '"Vazirmatn"',
            "Tahoma",
            '"Segoe UI"',
            "Arial",
            "sans-serif",
        ].join(", ");

        calendar
            .querySelectorAll("option")
            .forEach(
                function (option) {
                    option.textContent =
                        toPersianDigits(
                            option.textContent
                        );
                }
            );

        const walker =
            document.createTreeWalker(
                calendar,
                NodeFilter.SHOW_TEXT
            );

        const nodes = [];

        let node = walker.nextNode();

        while (node) {
            nodes.push(node);
            node = walker.nextNode();
        }

        nodes.forEach(
            function (textNode) {
                const parent =
                    textNode.parentElement;

                if (
                    parent
                    && parent.matches(
                        "script, style"
                    )
                ) {
                    return;
                }

                textNode.nodeValue =
                    toPersianDigits(
                        textNode.nodeValue
                    );
            }
        );
    }

    let translationScheduled = false;

    function translateVisibleCalendars() {
        translationScheduled = false;

        configureDatepicker();

        findCalendarRoots().forEach(
            translateCalendar
        );
    }

    function scheduleCalendarTranslation() {
        if (translationScheduled) {
            return;
        }

        translationScheduled = true;

        window.requestAnimationFrame(
            function () {
                translateVisibleCalendars();

                window.setTimeout(
                    translateVisibleCalendars,
                    30
                );

                window.setTimeout(
                    translateVisibleCalendars,
                    120
                );
            }
        );
    }

    function normalizeTimeText(value) {
        const digits = toLatinDigits(value)
            .replace(/[^0-9]/g, "")
            .slice(0, 4);

        if (!digits) {
            return "";
        }

        if (digits.length === 1) {
            return toPersianDigits(digits);
        }

        if (digits.length === 2) {
            return toPersianDigits(
                digits + ":"
            );
        }

        return toPersianDigits(
            digits.slice(0, 2)
            + ":"
            + digits.slice(2)
        );
    }

    function validateTimeInput(input) {
        const latin = toLatinDigits(
            input.value
        ).trim();

        if (!latin) {
            input.setCustomValidity("");
            return true;
        }

        const match =
            /^([0-9]{2}):([0-9]{2})$/.exec(
                latin
            );

        const isValid = Boolean(
            match
            && Number(match[1]) <= 23
            && Number(match[2]) <= 59
        );

        input.setCustomValidity(
            isValid
                ? ""
                : "زمان را به صورت ۱۴:۳۰ وارد کنید."
        );

        return isValid;
    }

    function configureTimeInput() {
        const input =
            document.getElementById(
                "id_published_at_1"
            );

        if (!input) {
            return;
        }

        /*
         * این ورودی فقط برای زمان است؛ بنابراین اتصال
         * تقویم جلالی و حالت فقط‌خواندنی از آن حذف می‌شود.
         * فیلد تاریخ بدون تغییر باقی می‌ماند.
         */
        Array.from(input.attributes).forEach(
            function (attribute) {
                const name =
                    attribute.name.toLowerCase();

                if (
                    name === "data-jdp"
                    || name.startsWith(
                        "data-jdp-"
                    )
                    || name.startsWith(
                        "data-jalali"
                    )
                ) {
                    input.removeAttribute(
                        attribute.name
                    );
                }
            }
        );

        input.type = "text";
        input.readOnly = false;
        input.disabled = false;

        input.removeAttribute("readonly");
        input.removeAttribute("disabled");
        input.removeAttribute("aria-readonly");

        input.classList.add(
            "project-time-input"
        );

        input.maxLength = 5;
        input.inputMode = "numeric";
        input.autocomplete = "off";
        input.dir = "ltr";

        if (input.value) {
            input.value =
                normalizeTimeText(
                    input.value
                );
        }

        /*
         * در اجرای دوباره اسکریپت، رویدادها تکراری
         * ثبت نمی‌شوند؛ اما ویژگی‌های ورودی همچنان
         * در هر اجرا اصلاح می‌شوند.
         */
        if (
            input.dataset
                .projectTimeConfigured
            === "true"
        ) {
            return;
        }

        input.dataset
            .projectTimeConfigured =
            "true";

        input.addEventListener(
            "keydown",
            function (event) {
                /*
                 * وقتی مقدار به شکل «۱۴:» است، Backspace
                 * باید رقم دوم ساعت را هم قابل حذف کند.
                 */
                if (
                    event.key === "Backspace"
                    && input.selectionStart
                        === input.value.length
                    && input.selectionEnd
                        === input.value.length
                    && input.value.endsWith(":")
                ) {
                    event.preventDefault();

                    const digits =
                        toLatinDigits(
                            input.value
                        )
                            .replace(
                                /[^0-9]/g,
                                ""
                            )
                            .slice(0, -1);

                    input.value =
                        normalizeTimeText(
                            digits
                        );

                    validateTimeInput(input);
                }
            }
        );

        input.addEventListener(
            "input",
            function () {
                input.value =
                    normalizeTimeText(
                        input.value
                    );

                validateTimeInput(input);

                input.setSelectionRange(
                    input.value.length,
                    input.value.length
                );
            }
        );

        input.addEventListener(
            "blur",
            function () {
                validateTimeInput(input);
            }
        );

        const form =
            input.closest("form");

        if (
            form
            && form.dataset
                .projectTimeConfigured
                !== "true"
        ) {
            form.dataset
                .projectTimeConfigured =
                "true";

            form.addEventListener(
                "submit",
                function (event) {
                    if (
                        !validateTimeInput(
                            input
                        )
                    ) {
                        event.preventDefault();

                        input.reportValidity();

                        return;
                    }

                    input.value =
                        toLatinDigits(
                            input.value
                        );
                }
            );
        }

        document.querySelectorAll(
            (
                ".form-row.field-published_at "
                + ".datetimeshortcuts, "
                + "[id^='clockbox']"
            )
        ).forEach(
            function (element) {
                element.remove();
            }
        );
    }

    function start() {
        configureTimeInput();
        configureDatepicker();
        scheduleCalendarTranslation();

        document.addEventListener(
            "focusin",
            function (event) {
                if (
                    event.target
                    instanceof HTMLInputElement
                    && event.target.matches(
                        "input[data-jdp]"
                    )
                ) {
                    configureDatepicker();
                    scheduleCalendarTranslation();
                }
            },
            true
        );

        document.addEventListener(
            "pointerdown",
            function (event) {
                if (
                    event.target
                    instanceof HTMLInputElement
                    && event.target.matches(
                        "input[data-jdp]"
                    )
                ) {
                    configureDatepicker();
                }
            },
            true
        );

        /*
         * ناظر سراسری عمداً استفاده نشده
         * تا فرم مدیریت کند نشود.
         */
    }

    if (
        document.readyState === "loading"
    ) {
        document.addEventListener(
            "DOMContentLoaded",
            start,
            {
                once: true,
            }
        );
    } else {
        start();
    }
}());