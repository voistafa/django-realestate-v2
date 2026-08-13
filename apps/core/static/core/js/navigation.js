"use strict";

document.addEventListener("DOMContentLoaded", () => {
    const navigationLinks = Array.from(
        document.querySelectorAll(
            ".main-navigation a[data-nav]",
        ),
    );

    if (navigationLinks.length === 0) {
        return;
    }


    function normalizePath(pathname) {
        if (!pathname || pathname === "/") {
            return "/";
        }

        return pathname.replace(/\/+$/, "");
    }


    function getCurrentHash() {
        return window.location.hash
            .replace(/^#/, "")
            .trim()
            .toLowerCase();
    }


    function getActiveNavigationKey() {
        const currentPath = normalizePath(
            window.location.pathname,
        );

        const currentHash = getCurrentHash();


        /*
         * صفحه املاک و تمام زیرصفحه‌های آن
         */

        if (
            currentPath === "/properties"
            || currentPath.startsWith("/properties/")
        ) {
            return "properties";
        }


        /*
         * صفحه پروژه‌ها و تمام زیرصفحه‌های آن
         */

        if (
            currentPath === "/projects"
            || currentPath.startsWith("/projects/")
        ) {
            return "projects";
        }


        /*
         * صفحه مشاوران و تمام زیرصفحه‌های آن
         */

        if (
            currentPath === "/agents"
            || currentPath.startsWith("/agents/")
        ) {
            return "agents";
        }


        /*
         * صفحه درباره ما
         */

        if (
            currentPath === "/about"
            || currentPath.startsWith("/about/")
        ) {
            return "about";
        }


        /*
         * صفحه تماس با ما
         */

        if (
            currentPath === "/contact"
            || currentPath.startsWith("/contact/")
        ) {
            return "contact";
        }


        /*
         * صفحه اصلی و بخش‌های داخلی آن
         */

        if (currentPath === "/") {
            const validHomeSections = [
                "projects",
                "agents",
                "about",
                "contact",
            ];

            if (validHomeSections.includes(currentHash)) {
                return currentHash;
            }

            return "home";
        }


        return "";
    }


    function clearActiveNavigation() {
        navigationLinks.forEach((link) => {
            link.classList.remove("is-active");
            link.removeAttribute("aria-current");
        });
    }


    function setActiveNavigation() {
        const activeNavigationKey =
            getActiveNavigationKey();

        clearActiveNavigation();

        if (!activeNavigationKey) {
            return;
        }

        const activeLink = navigationLinks.find(
            (link) =>
                link.dataset.nav === activeNavigationKey,
        );

        if (!activeLink) {
            return;
        }

        activeLink.classList.add("is-active");
        activeLink.setAttribute(
            "aria-current",
            "page",
        );
    }


    /*
     * اجرای اولیه پس از بارگذاری صفحه
     */

    setActiveNavigation();


    /*
     * تغییر گزینه فعال هنگام تغییر بخش بعد از #
     */

    window.addEventListener(
        "hashchange",
        setActiveNavigation,
    );


    /*
     * تغییر گزینه فعال هنگام رفت‌وبرگشت مرورگر
     */

    window.addEventListener(
        "popstate",
        setActiveNavigation,
    );


    /*
     * اجرای مجدد هنگام برگشت صفحه از حافظه مرورگر
     */

    window.addEventListener(
        "pageshow",
        setActiveNavigation,
    );


    /*
     * تغییر فوری گزینه فعال هنگام کلیک روی منو
     */

    navigationLinks.forEach((link) => {
        link.addEventListener("click", () => {
            window.setTimeout(
                setActiveNavigation,
                0,
            );
        });
    });
});