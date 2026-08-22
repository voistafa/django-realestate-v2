(function () {
    "use strict";

    function initializeActionSelect(select) {
        if (select.dataset.customActionReady === "true") {
            return;
        }

        select.dataset.customActionReady = "true";

        /*
         * Select اصلی Django برای ارسال مقدار فرم باقی می‌ماند،
         * ولی از دید کاربر مخفی می‌شود.
         */
        select.hidden = true;

        select.style.setProperty(
            "display",
            "none",
            "important"
        );

        const wrapper = document.createElement("div");
        wrapper.className = "admin-action-picker";

        const trigger = document.createElement("button");
        trigger.type = "button";
        trigger.className = "admin-action-picker__trigger";
        trigger.setAttribute("aria-haspopup", "listbox");
        trigger.setAttribute("aria-expanded", "false");

        const triggerText = document.createElement("span");
        triggerText.className =
            "admin-action-picker__text";

        const arrow = document.createElement("span");
        arrow.className =
            "admin-action-picker__arrow";
        arrow.setAttribute("aria-hidden", "true");
        arrow.textContent = "⌄";

        trigger.appendChild(triggerText);
        trigger.appendChild(arrow);

        const menu = document.createElement("div");
        menu.className = "admin-action-picker__menu";
        menu.setAttribute("role", "listbox");
        menu.hidden = true;

        const optionButtons = [];

        function updateTrigger() {
            const selected =
                select.options[select.selectedIndex];

            if (
                selected &&
                selected.value !== ""
            ) {
                triggerText.textContent =
                    selected.textContent.trim();
            } else {
                triggerText.textContent =
                    "گزینه مدنظر را انتخاب کنید";
            }
        }

        function closeMenu(returnFocus) {
            menu.hidden = true;

            trigger.setAttribute(
                "aria-expanded",
                "false"
            );

            if (returnFocus) {
                trigger.focus();
            }
        }

        function openMenu() {
            menu.hidden = false;

            trigger.setAttribute(
                "aria-expanded",
                "true"
            );

            const selectedButton =
                optionButtons.find(function (button) {
                    return (
                        button.dataset.value ===
                        select.value
                    );
                });

            const target =
                selectedButton || optionButtons[0];

            if (target) {
                window.requestAnimationFrame(
                    function () {
                        target.focus();
                    }
                );
            }
        }

        function choose(value) {
            select.value = value;

            select.dispatchEvent(
                new Event("change", {
                    bubbles: true
                })
            );

            updateTrigger();
            closeMenu(true);
        }

        Array.from(select.options).forEach(
            function (option) {
                if (
                    !option.value ||
                    option.disabled
                ) {
                    return;
                }

                const button =
                    document.createElement("button");

                button.type = "button";
                button.className =
                    "admin-action-picker__option";

                button.dataset.value = option.value;
                button.setAttribute("role", "option");

                button.textContent =
                    option.textContent.trim();

                button.addEventListener(
                    "click",
                    function () {
                        choose(option.value);
                    }
                );

                button.addEventListener(
                    "keydown",
                    function (event) {
                        const index =
                            optionButtons.indexOf(
                                button
                            );

                        if (event.key === "ArrowDown") {
                            event.preventDefault();

                            const next =
                                optionButtons[
                                    Math.min(
                                        index + 1,
                                        optionButtons.length - 1
                                    )
                                ];

                            if (next) {
                                next.focus();
                            }
                        }

                        if (event.key === "ArrowUp") {
                            event.preventDefault();

                            const previous =
                                optionButtons[
                                    Math.max(
                                        index - 1,
                                        0
                                    )
                                ];

                            if (previous) {
                                previous.focus();
                            }
                        }

                        if (event.key === "Escape") {
                            event.preventDefault();
                            closeMenu(true);
                        }
                    }
                );

                menu.appendChild(button);
                optionButtons.push(button);
            }
        );

        trigger.addEventListener(
            "click",
            function () {
                if (menu.hidden) {
                    openMenu();
                } else {
                    closeMenu(false);
                }
            }
        );

        trigger.addEventListener(
            "keydown",
            function (event) {
                if (
                    event.key === "ArrowDown" ||
                    event.key === "Enter" ||
                    event.key === " "
                ) {
                    event.preventDefault();
                    openMenu();
                }

                if (event.key === "Escape") {
                    closeMenu(false);
                }
            }
        );

        document.addEventListener(
            "click",
            function (event) {
                if (!wrapper.contains(event.target)) {
                    closeMenu(false);
                }
            }
        );

        select.addEventListener(
            "change",
            updateTrigger
        );

        select.insertAdjacentElement(
            "afterend",
            wrapper
        );

        wrapper.appendChild(trigger);
        wrapper.appendChild(menu);

        updateTrigger();
    }

    function start() {
        const selects = document.querySelectorAll(
            '#changelist-form .actions select[name="action"]'
        );

        selects.forEach(
            initializeActionSelect
        );
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