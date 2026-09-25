"use strict";


const customSelectInstances = [];


document.addEventListener("DOMContentLoaded", () => {
    initializePriceInputs();
    initializeCustomSelects();
    initializeSearchInput();
    initializePlaceholderDigits();
});

function initializePlaceholderDigits() {
    const inputs = document.querySelectorAll(
        ".js-price-input",
    );

    inputs.forEach((input) => {
        if (input.placeholder) {
            input.placeholder = toPersianDigits(
                input.placeholder,
            );
        }
    });
}

function initializeSearchInput() {
    const searchInput = document.querySelector(
        "#property-search",
    );

    if (!searchInput) {
        return;
    }

    const convertSearchDigits = () => {
    const before = searchInput.value;

    const after = toPersianDigits(
        searchInput.value,
    );

    console.log("BEFORE:", before);
    console.log("AFTER:", after);

    searchInput.value = after;
};

    convertSearchDigits();

    searchInput.addEventListener(
        "input",
        convertSearchDigits,
    );

    searchInput.addEventListener(
        "change",
        convertSearchDigits,
    );

    searchInput.addEventListener(
        "keyup",
        convertSearchDigits,
    );
}

/* ==================================================
   Price Inputs
================================================== */

function normalizeDigits(value) {
    const digitMap = {
        "۰": "0",
        "۱": "1",
        "۲": "2",
        "۳": "3",
        "۴": "4",
        "۵": "5",
        "۶": "6",
        "۷": "7",
        "۸": "8",
        "۹": "9",

        "٠": "0",
        "١": "1",
        "٢": "2",
        "٣": "3",
        "٤": "4",
        "٥": "5",
        "٦": "6",
        "٧": "7",
        "٨": "8",
        "٩": "9",
    };

    return String(value).replace(
        /[۰-۹٠-٩]/g,
        (digit) => digitMap[digit] ?? digit,
    );
}


function extractNumericValue(value) {
    return normalizeDigits(value).replace(/[^\d]/g, "");
}


function formatPriceValue(value) {
    const numericValue = extractNumericValue(value);

    if (!numericValue) {
        return "";
    }

    return numericValue.replace(
        /\B(?=(\d{3})+(?!\d))/g,
        ",",
    );
}


function toPersianDigits(value) {
    const persianDigits = "۰۱۲۳۴۵۶۷۸۹";

    return String(value).replace(
        /\d/g,
        (digit) => persianDigits[digit],
    );
}


function initializePriceInputs() {
    const priceInputs = document.querySelectorAll(
        ".js-price-input",
    );

    priceInputs.forEach((input) => {
        if (input.placeholder) {
            input.placeholder = toPersianDigits(
                input.placeholder,
            );
        }
    });

    priceInputs.forEach((input) => {
        input.value = toPersianDigits(
            formatPriceValue(input.value),
        );

        input.addEventListener("input", () => {
            const formattedValue = formatPriceValue(
                input.value,
            );

            input.value = toPersianDigits(
                formattedValue,
            );
        });

        input.addEventListener("paste", () => {
            window.setTimeout(() => {
                input.value = toPersianDigits(
                    formatPriceValue(input.value),
                );
            }, 0);
        });

        input.addEventListener("blur", () => {
            input.value = toPersianDigits(
                formatPriceValue(input.value),
            );
        });
    });

    document
        .querySelectorAll(".property-filter-form")
        .forEach((form) => {
            form.addEventListener("submit", () => {
                form
                    .querySelectorAll(".js-price-input")
                    .forEach((input) => {
                        input.value = extractNumericValue(
                            input.value,
                        );
                    });
            });
        });
}


/* ==================================================
   Custom Select Initialization
================================================== */

function initializeCustomSelects() {
    const nativeSelects = document.querySelectorAll(
        ".js-custom-select",
    );

    nativeSelects.forEach(
        (nativeSelect, selectIndex) => {
            createCustomSelect(
                nativeSelect,
                selectIndex,
            );
        },
    );


    document.addEventListener("click", (event) => {
        customSelectInstances.forEach((instance) => {
            const clickedInsideWrapper =
                instance.wrapper.contains(event.target);

            const clickedInsideMenu =
                instance.menu.contains(event.target);

            if (
                !clickedInsideWrapper
                && !clickedInsideMenu
            ) {
                closeCustomSelect(instance);
            }
        });
    });


    document.addEventListener("keydown", (event) => {
        if (event.key !== "Escape") {
            return;
        }

        customSelectInstances.forEach((instance) => {
            if (
                instance.wrapper.classList.contains(
                    "is-open",
                )
            ) {
                closeCustomSelect(instance);
                instance.trigger.focus();
            }
        });
    });


    window.addEventListener(
        "resize",
        repositionOpenCustomSelects,
    );


    window.addEventListener(
        "scroll",
        repositionOpenCustomSelects,
        true,
    );


    if (window.visualViewport) {
        window.visualViewport.addEventListener(
            "resize",
            repositionOpenCustomSelects,
        );

        window.visualViewport.addEventListener(
            "scroll",
            repositionOpenCustomSelects,
        );
    }
}


/* ==================================================
   Custom Select Creation
================================================== */

function createCustomSelect(
    nativeSelect,
    selectIndex,
) {
    const wrapper = document.createElement("div");

    wrapper.className = "custom-select";


    const trigger = document.createElement("button");

    trigger.type = "button";
    trigger.className = "custom-select__trigger";
    trigger.id = `${nativeSelect.id}-trigger`;


    const menu = document.createElement("div");

    menu.className = "custom-select__menu";
    menu.id = `custom-select-menu-${selectIndex}`;

    menu.setAttribute("role", "listbox");
    menu.setAttribute("dir", "rtl");
    menu.setAttribute("aria-hidden", "true");


    trigger.setAttribute(
        "aria-haspopup",
        "listbox",
    );

    trigger.setAttribute(
        "aria-expanded",
        "false",
    );

    trigger.setAttribute(
        "aria-controls",
        menu.id,
    );


    const relatedLabel = document.querySelector(
        `label[for="${nativeSelect.id}"]`,
    );

    if (relatedLabel) {
        relatedLabel.htmlFor = trigger.id;
    }


    nativeSelect.parentNode.insertBefore(
        wrapper,
        nativeSelect,
    );

    wrapper.appendChild(nativeSelect);
    wrapper.appendChild(trigger);

    document.body.appendChild(menu);


    nativeSelect.classList.add(
        "custom-select__native",
    );

    nativeSelect.tabIndex = -1;
    nativeSelect.setAttribute("aria-hidden", "true");


    const instance = {
        wrapper,
        nativeSelect,
        trigger,
        menu,
        optionButtons: [],
    };

    customSelectInstances.push(instance);


    const options = Array.from(
        nativeSelect.options,
    );


    options.forEach(
        (nativeOption, optionIndex) => {
            const optionButton =
                document.createElement("button");

            optionButton.type = "button";
            optionButton.className =
                "custom-select__option";

            optionButton.id =
                `${menu.id}-option-${optionIndex}`;

            optionButton.textContent =
                nativeOption.textContent.trim();

            optionButton.dataset.value =
                nativeOption.value;

            optionButton.setAttribute(
                "role",
                "option",
            );


            const isSelected =
                nativeOption.selected;

            optionButton.classList.toggle(
                "is-selected",
                isSelected,
            );

            optionButton.setAttribute(
                "aria-selected",
                String(isSelected),
            );


            optionButton.addEventListener(
                "click",
                () => {
                    selectCustomOption(
                        instance,
                        optionButton,
                    );
                },
            );


            optionButton.addEventListener(
                "keydown",
                (event) => {
                    handleOptionKeyboard(
                        event,
                        instance,
                        optionIndex,
                    );
                },
            );


            instance.optionButtons.push(
                optionButton,
            );

            menu.appendChild(optionButton);
        },
    );


    updateCustomSelectLabel(instance);


    trigger.addEventListener("click", () => {
        toggleCustomSelect(instance);
    });


    trigger.addEventListener(
        "keydown",
        (event) => {
            handleTriggerKeyboard(
                event,
                instance,
            );
        },
    );


    nativeSelect.addEventListener(
        "change",
        () => {
            updateCustomSelectLabel(instance);
            synchronizeSelectedOption(instance);
        },
    );
}


/* ==================================================
   Custom Select Selection
================================================== */

function selectCustomOption(
    instance,
    optionButton,
) {
    instance.nativeSelect.value =
        optionButton.dataset.value;

    instance.nativeSelect.dispatchEvent(
        new Event("change", {
            bubbles: true,
        }),
    );

    closeCustomSelect(instance);
    instance.trigger.focus();
}


function updateCustomSelectLabel(instance) {
    const selectedIndex =
        instance.nativeSelect.selectedIndex;

    const selectedOption =
        instance.nativeSelect.options[
            selectedIndex
        ];

    instance.trigger.textContent = selectedOption
        ? selectedOption.textContent.trim()
        : "";
}


function synchronizeSelectedOption(instance) {
    instance.optionButtons.forEach(
        (optionButton) => {
            const isSelected =
                optionButton.dataset.value
                === instance.nativeSelect.value;

            optionButton.classList.toggle(
                "is-selected",
                isSelected,
            );

            optionButton.setAttribute(
                "aria-selected",
                String(isSelected),
            );
        },
    );
}


/* ==================================================
   Custom Select Open and Close
================================================== */

function toggleCustomSelect(instance) {
    const isOpen =
        instance.wrapper.classList.contains(
            "is-open",
        );

    if (isOpen) {
        closeCustomSelect(instance);
        return;
    }

    openCustomSelect(instance);
}


function openCustomSelect(instance) {
    customSelectInstances.forEach(
        (otherInstance) => {
            if (otherInstance !== instance) {
                closeCustomSelect(otherInstance);
            }
        },
    );


    instance.wrapper.classList.add("is-open");

    instance.menu.classList.add(
        "is-visible",
    );

    instance.menu.setAttribute(
        "aria-hidden",
        "false",
    );

    instance.trigger.setAttribute(
        "aria-expanded",
        "true",
    );


    positionCustomSelectMenu(instance);


    window.requestAnimationFrame(() => {
        scrollSelectedOptionIntoView(instance);
    });
}


function closeCustomSelect(instance) {
    instance.wrapper.classList.remove(
        "is-open",
    );

    instance.menu.classList.remove(
        "is-visible",
    );

    instance.menu.setAttribute(
        "aria-hidden",
        "true",
    );

    instance.trigger.setAttribute(
        "aria-expanded",
        "false",
    );

    instance.menu.style.visibility = "";
}


/* ==================================================
   Custom Select Position
================================================== */

function positionCustomSelectMenu(instance) {
    if (
        !instance.menu.classList.contains(
            "is-visible",
        )
    ) {
        return;
    }


    const triggerRect =
        instance.trigger.getBoundingClientRect();

    const viewportWidth =
        window.visualViewport?.width
        ?? window.innerWidth;

    const viewportHeight =
        window.visualViewport?.height
        ?? window.innerHeight;

    const viewportOffsetLeft =
        window.visualViewport?.offsetLeft
        ?? 0;

    const viewportOffsetTop =
        window.visualViewport?.offsetTop
        ?? 0;

    const viewportMargin = 12;
    const menuGap = 8;
    const preferredMaximumHeight = 290;


    const maximumMenuWidth = Math.max(
        220,
        viewportWidth - (viewportMargin * 2),
    );

    const menuWidth = Math.min(
        triggerRect.width,
        maximumMenuWidth,
    );


    let menuLeft = triggerRect.left;

    const minimumLeft =
        viewportOffsetLeft + viewportMargin;

    const maximumLeft =
        viewportOffsetLeft
        + viewportWidth
        - menuWidth
        - viewportMargin;

    menuLeft = Math.max(
        minimumLeft,
        Math.min(menuLeft, maximumLeft),
    );


    instance.menu.style.visibility = "hidden";

    instance.menu.style.width =
        `${Math.round(menuWidth)}px`;

    instance.menu.style.left =
        `${Math.round(menuLeft)}px`;

    instance.menu.style.right = "auto";
    instance.menu.style.top = "0px";

    instance.menu.style.maxHeight =
        `${preferredMaximumHeight}px`;


    const naturalMenuHeight = Math.min(
        instance.menu.scrollHeight,
        preferredMaximumHeight,
    );


    const viewportTop =
        viewportOffsetTop + viewportMargin;

    const viewportBottom =
        viewportOffsetTop
        + viewportHeight
        - viewportMargin;


    const spaceBelow =
        viewportBottom
        - triggerRect.bottom
        - menuGap;

    const spaceAbove =
        triggerRect.top
        - viewportTop
        - menuGap;


    const shouldOpenAbove =
        spaceBelow < naturalMenuHeight
        && spaceAbove > spaceBelow;


    const availableSpace = shouldOpenAbove
        ? spaceAbove
        : spaceBelow;


    const finalMaximumHeight = Math.max(
        90,
        Math.min(
            preferredMaximumHeight,
            availableSpace,
        ),
    );


    instance.menu.style.maxHeight =
        `${Math.round(finalMaximumHeight)}px`;


    const renderedMenuHeight = Math.min(
        instance.menu.scrollHeight,
        finalMaximumHeight,
    );


    let menuTop;

    if (shouldOpenAbove) {
        menuTop =
            triggerRect.top
            - renderedMenuHeight
            - menuGap;
    } else {
        menuTop =
            triggerRect.bottom
            + menuGap;
    }


    const minimumTop = viewportTop;

    const maximumTop =
        viewportBottom
        - renderedMenuHeight;


    menuTop = Math.max(
        minimumTop,
        Math.min(menuTop, maximumTop),
    );


    instance.menu.style.top =
        `${Math.round(menuTop)}px`;

    instance.menu.style.visibility =
        "visible";
}


function repositionOpenCustomSelects() {
    customSelectInstances.forEach(
        (instance) => {
            if (
                instance.wrapper.classList.contains(
                    "is-open",
                )
            ) {
                positionCustomSelectMenu(instance);
            }
        },
    );
}


/* ==================================================
   Custom Select Keyboard Controls
================================================== */

function handleTriggerKeyboard(
    event,
    instance,
) {
    const openKeys = [
        "ArrowDown",
        "ArrowUp",
        "Enter",
        " ",
    ];


    if (openKeys.includes(event.key)) {
        event.preventDefault();

        if (
            !instance.wrapper.classList.contains(
                "is-open",
            )
        ) {
            openCustomSelect(instance);
        }

        focusSelectedOption(instance);
        return;
    }


    if (event.key === "Escape") {
        event.preventDefault();
        closeCustomSelect(instance);
    }
}


function handleOptionKeyboard(
    event,
    instance,
    currentIndex,
) {
    const options = instance.optionButtons;


    if (event.key === "ArrowDown") {
        event.preventDefault();

        const nextIndex =
            currentIndex >= options.length - 1
                ? 0
                : currentIndex + 1;

        options[nextIndex]?.focus();
        return;
    }


    if (event.key === "ArrowUp") {
        event.preventDefault();

        const previousIndex =
            currentIndex <= 0
                ? options.length - 1
                : currentIndex - 1;

        options[previousIndex]?.focus();
        return;
    }


    if (
        event.key === "Enter"
        || event.key === " "
    ) {
        event.preventDefault();

        selectCustomOption(
            instance,
            options[currentIndex],
        );

        return;
    }


    if (event.key === "Escape") {
        event.preventDefault();

        closeCustomSelect(instance);
        instance.trigger.focus();

        return;
    }


    if (event.key === "Home") {
        event.preventDefault();
        options[0]?.focus();

        return;
    }


    if (event.key === "End") {
        event.preventDefault();
        options.at(-1)?.focus();

        return;
    }


    if (event.key === "Tab") {
        closeCustomSelect(instance);
    }
}


function focusSelectedOption(instance) {
    const selectedOption =
        instance.menu.querySelector(
            ".custom-select__option.is-selected",
        )
        || instance.menu.querySelector(
            ".custom-select__option",
        );

    selectedOption?.focus();
}


function scrollSelectedOptionIntoView(instance) {
    const selectedOption =
        instance.menu.querySelector(
            ".custom-select__option.is-selected",
        );

    selectedOption?.scrollIntoView({
        block: "nearest",
        inline: "nearest",
    });
}